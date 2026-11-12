
import os
import io
import time
import base64
import logging

import torch
import runpod
from diffusers import FluxPipeline

# Configure application logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("flux-serverless")

# Model configuration
MODEL_ID = os.getenv(
    "MODEL_ID",
    "black-forest-labs/FLUX.1-dev"
)

HF_TOKEN = os.getenv("HF_TOKEN")
pipeline = None


def load_model():
    """Load the FLUX model once per worker."""
    global pipeline

    if pipeline is not None:
        return pipeline

    if not torch.cuda.is_available():
        raise RuntimeError("CUDA GPU is unavailable")

    logger.info("Loading model: %s", MODEL_ID)

    pipeline = FluxPipeline.from_pretrained(
        MODEL_ID,
        torch_dtype=torch.bfloat16,
        token=HF_TOKEN
    )

    # Use CPU offloading when requested to save GPU VRAM
    if os.getenv("CPU_OFFLOAD", "false").lower() == "true":
        pipeline.enable_model_cpu_offload()
    else:
        pipeline.to("cuda")

    logger.info("FLUX model loaded successfully")
    return pipeline


def handler(job):
    """Process one RunPod serverless inference request."""
    start_time = time.time()

    try:
        data = job.get("input", {})

        if not isinstance(data, dict):
            return {"error": "Input must be a JSON object"}

        prompt = data.get("prompt")

        if not isinstance(prompt, str) or not prompt.strip():
            return {"error": "A non-empty text prompt is required"}

        if len(prompt) > 1000:
            return {"error": "Prompt cannot exceed 1000 characters"}

        width = data.get("width", 512)
        height = data.get("height", 512)
        steps = data.get("num_inference_steps", 20)
        seed = data.get("seed", 42)

        if (
            type(width) is not int
            or type(height) is not int
            or width not in (512, 768, 1024)
            or height not in (512, 768, 1024)
        ):
            return {"error": "Dimensions must be 512, 768 or 1024"}

        if type(steps) is not int or not 1 <= steps <= 50:
            return {"error": "Steps must be between 1 and 50"}

        if type(seed) is not int or not 0 <= seed < 2**63:
            return {"error": "Seed must be a non-negative integer"}

        logger.info(
            "Generating image: %sx%s, steps=%s",
            width, height, steps
        )

        model = load_model()

        generator = torch.Generator(
            device="cpu"
        ).manual_seed(seed)

        with torch.inference_mode():
            result = model(
                prompt=prompt,
                width=width,
                height=height,
                num_inference_steps=steps,
                guidance_scale=3.5,
                max_sequence_length=512,
                generator=generator
            )

        image = result.images[0]

        # Convert generated image into Base64 PNG
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")

        image_base64 = base64.b64encode(
            buffer.getvalue()
        ).decode("utf-8")

        duration = round(time.time() - start_time, 2)

        logger.info(
            "Image generated successfully in %s seconds",
            duration
        )

        return {
            "status": "success",
            "model": MODEL_ID,
            "image_base64": image_base64,
            "format": "png",
            "width": width,
            "height": height,
            "seed": seed,
            "execution_time_seconds": duration
        }

    except torch.cuda.OutOfMemoryError:
        logger.exception("GPU out of memory")
        return {"error": "GPU out of memory"}

    except Exception:
        logger.exception("Inference request failed")
        return {"error": "Image generation failed; check worker logs"}


if __name__ == "__main__":
    runpod.serverless.start({"handler": handler})

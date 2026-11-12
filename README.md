# RunPod Serverless FLUX.1-dev Image Generation

## Project Overview

This project demonstrates the deployment of the FLUX.1-dev text-to-image generation model using RunPod Serverless GPU infrastructure.

The application uses a custom Python inference handler, Hugging Face Diffusers, PyTorch, and Docker. It accepts a text prompt through a queue-based serverless endpoint and returns a generated PNG image as Base64-encoded data.

## Technology Stack

- Python
- RunPod Serverless SDK
- PyTorch
- Hugging Face Diffusers
- FLUX.1-dev
- Docker and Docker Hub
- NVIDIA A40 GPU
- RunPod Network Volume

## Architecture

Client Request → RunPod Serverless API → GPU Worker → Docker Container → Python Handler → FLUX.1-dev → Generated Image → API Response

## Sample Request

```json
{
  "input": {
    "prompt": "A futuristic city at sunset with flying cars, cinematic lighting",
    "width": 512,
    "height": 512,
    "num_inference_steps": 20,
    "seed": 42
  }
}
```

## Verified Results

| Metric | Result |
|---|---|
| Request Status | COMPLETED |
| Model | FLUX.1-dev |
| Image Resolution | 512 × 512 |
| Image Format | PNG |
| Queue Delay | 13.01 seconds |
| Handler Execution Time | 64.66 seconds |
| Output Image Size | Approximately 333 KB |

These metrics reflect one successful inference request.

## Troubleshooting

During initial testing, image generation failed with:

`OSError: [Errno 28] No space left on device`

The error occurred while downloading the FLUX.1-dev model files.

To resolve it, a 150 GB RunPod network volume was created and attached to the endpoint. The Hugging Face cache was configured to use `/runpod-volume/huggingface`.

After this change, the inference request completed successfully.

## Deployment Configuration

- Endpoint: `flux-serverless-assessment`
- GPU: NVIDIA A40, 48 GB
- Max workers: 1
- Active workers: 0
- Execution timeout: 600 seconds
- Model storage: 150 GB RunPod network volume

## Docker Image

**Docker Hub:** https://hub.docker.com/r/akhila124/runpod-flux-serverless

**Image:** `akhila124/runpod-flux-serverless:v1`

The Docker image packages the Python handler and dependencies. Model weights are downloaded and cached on the configured RunPod storage volume during runtime.

## Test Evidence

Successful inference and deployment screenshots are available in the `evidence/` folder.

- `flux-generated-image.png`
- `successful-api-response.png`
- `generated-image-preview.png`
- `endpoint-configuration.png`
- `docker-image.png`

## Security

API credentials and Hugging Face access tokens are excluded from the repository. Runtime credentials must be configured securely through RunPod endpoint settings.

## References

- https://docs.runpod.io/serverless/get-started
- https://huggingface.co/black-forest-labs/FLUX.1-dev

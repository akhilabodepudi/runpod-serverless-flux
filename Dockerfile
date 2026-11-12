
# CUDA-enabled PyTorch base image
FROM pytorch/pytorch:2.5.1-cuda12.4-cudnn9-runtime

# Set the working directory
WORKDIR /app

# Install application dependencies
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy inference handler
COPY handler.py .

# Set model configuration
ENV PYTHONUNBUFFERED=1
ENV MODEL_ID=black-forest-labs/FLUX.1-dev
ENV HF_HOME=/app/model-cache

# Start the RunPod serverless worker
CMD ["python", "-u", "handler.py"]

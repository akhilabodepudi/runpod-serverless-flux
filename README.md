# RunPod Serverless Flux

A minimal RunPod serverless project scaffold for local testing and deployment.

## Project structure

- `handler.py` - serverless request handler
- `Dockerfile` - container definition for deployment
- `requirements.txt` - Python dependencies
- `test_input.json` - sample payload for local validation
- `test_endpoint.py` - local handler smoke test
- `.env.example` - template for environment variables
- `docs/` - architecture and documentation artifacts
- `evidence/` - screenshots and generated outputs

## Quick start

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python test_endpoint.py
```

## Docker build

```bash
docker build -t runpod-serverless-flux .
docker run --rm -p 8000:8000 runpod-serverless-flux
```

## Notes

This project is intentionally lightweight and can be extended with your model client, authentication layer, or custom inference pipeline.

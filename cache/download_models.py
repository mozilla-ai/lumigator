import os

from huggingface_hub import snapshot_download
from loguru import logger

logger.info("*** Inference models caching ***")

# Get the MODELS_CACHED environment variable (defaults to bart if not provided)
models_env = os.environ.get("MODELS_CACHED", "facebook/bart-large-cnn")
logger.info(f"Caching the following models: {models_env}")
logger.info("(this might take a while...)")

# Split by comma and strip whitespace
models = [model.strip() for model in models_env.split(",")]

for i, model in enumerate(models):
    model_path = snapshot_download(model, cache_dir="/home/ray/.cache/huggingface/hub")
    logger.info(f"Model {i + 1}/{len(models)} downloaded: {model}")

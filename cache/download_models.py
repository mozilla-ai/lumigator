import os

from huggingface_hub import snapshot_download

# Get the MODELS_CACHED environment variable (defaults to bart if not provided)
models_env = os.environ.get("MODELS_CACHED", "facebook/bart-large-cnn")
# Split by comma and strip whitespace
models = [model.strip() for model in models_env.split(",")]

for model in models:
    model_path = snapshot_download(model, cache_dir="/home/ray/.cache/huggingface/hub")
    print(f"Model {model} downloaded")

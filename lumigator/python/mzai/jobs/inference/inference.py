"""python job to run batch inference"""

import argparse
import json
from collections.abc import Iterable
from pathlib import Path

import s3fs
from datasets import load_from_disk
from inference_config import InferenceJobConfig
from loguru import logger
from model_clients import (
    BaseModelClient,
    HuggingFaceModelClient,
    MistralModelClient,
    OpenAIModelClient,
)
from paths import PathPrefix
from tqdm import tqdm


def predict(dataset_iterable: Iterable, model_client: BaseModelClient) -> list:
    predictions = []

    for sample_txt in dataset_iterable:
        predictions.append(model_client.predict(sample_txt))

    return predictions


def save_to_disk(local_path: Path, data_dict: dict):
    logger.info(f"Storing into {local_path}...")
    local_path.parent.mkdir(exist_ok=True, parents=True)
    with local_path.open("w") as f:
        json.dump(data_dict, f)


def save_to_s3(config: InferenceJobConfig, local_path: Path, storage_path: str):
    s3 = s3fs.S3FileSystem()
    if storage_path.endswith("/"):
        storage_path = "s3://" + str(
            Path(storage_path[5:]) / config.name / "inference_results.json"
        )
    logger.info(f"Storing into {storage_path}...")
    s3.put_file(local_path, storage_path)


def save_outputs(config: InferenceJobConfig, inference_results: dict) -> Path:
    storage_path = config.job.storage_path

    # generate local temp file ANYWAY:
    # - if storage_path is not provided, it will be stored and kept into a default dir
    # - if storage_path is provided AND saving to S3 is successful, local file is deleted
    local_path = Path(
        Path.home() / ".lumigator" / "results" / config.name / "inference_results.json"
    )

    try:
        save_to_disk(local_path, inference_results)

        # copy to s3 and return path
        if storage_path is not None and storage_path.startswith("s3://"):
            save_to_s3(config, local_path, storage_path)
            Path.unlink(local_path)
            Path.rmdir(local_path.parent)
            return storage_path
        else:
            return local_path

    except Exception as e:
        logger.error(e)


def run_inference(config: InferenceJobConfig) -> Path:
    # initialize output dictionary
    output = {}

    # Load dataset given its URI
    dataset = load_from_disk(config.dataset.path)

    # Limit dataset length if max_samples is specified
    max_samples = config.job.max_samples
    if max_samples is not None and max_samples > 0:
        if max_samples > len(dataset):
            logger.info(f"max_samples ({max_samples}) resized to dataset size ({len(dataset)})")
            max_samples = len(dataset)
        dataset = dataset.select(range(max_samples))

    # Enable / disable tqdm
    input_samples = dataset["examples"]
    dataset_iterable = tqdm(input_samples) if config.job.enable_tqdm else input_samples

    # Choose which model client to use
    if config.inference_server is not None:
        # a model *inference service* is passed
        base_url = config.inference_server.base_url
        output_model_name = config.inference_server.engine
        if "mistral" in base_url:
            # run the mistral client
            logger.info(f"Using Mistral client. Endpoint: {base_url}")
            model_client = MistralModelClient(base_url, config)
        else:
            # run the openai client
            logger.info(f"Using OAI client. Endpoint: {base_url}")
            model_client = OpenAIModelClient(base_url, config)
    elif config.hf_pipeline:
        if config.hf_pipeline.model_uri.startswith(PathPrefix.HUGGINGFACE):
            logger.info("Using HuggingFace client.")
            model_client = HuggingFaceModelClient(config)
            output_model_name = config.hf_pipeline.model
        else:
            raise ValueError("Unsupported model type.")
    else:
        raise NotImplementedError("Inference pipeline not supported.")

    # run inference
    output[config.job.output_field] = predict(dataset_iterable, model_client)
    output["examples"] = dataset["examples"]
    output["ground_truth"] = dataset["ground_truth"]
    output["model"] = output_model_name

    output_path = save_outputs(config, output)
    return output_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=str, help="Configuration in JSON format")
    args = parser.parse_args()

    if not args.config:
        parser.print_help()  # Print the usage message and exit
        err_str = "No input configuration provided. Please pass one using the --config flag"
        logger.error(err_str)
    else:
        config = InferenceJobConfig.model_validate_json(args.config)
        result_dataset_path = run_inference(config)
        logger.info(f"Inference results stored at {result_dataset_path}")

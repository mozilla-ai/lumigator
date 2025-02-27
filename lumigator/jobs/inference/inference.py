"""python job to run batch inference"""

import argparse
import json
from collections.abc import Iterable
from pathlib import Path

import s3fs
from datasets import load_from_disk
from inference_config import InferenceJobConfig
from loguru import logger
from model_clients import BaseModelClient, HuggingFaceModelClient, LiteLLMModelClient
from tqdm import tqdm
from utils import timer

from schemas import InferenceJobOutput, InferenceMetrics, JobOutput, PredictionResult


@timer
def predict(dataset_iterable: Iterable, model_client: BaseModelClient) -> list[PredictionResult]:
    predictions = []

    for sample_txt in dataset_iterable:
        predictions.append(model_client.predict(sample_txt))

    return predictions


def save_to_disk(local_path: Path, results: JobOutput):
    logger.info(f"Storing into {local_path}...")
    local_path.parent.mkdir(exist_ok=True, parents=True)
    with local_path.open("w") as f:
        json.dump(results.model_dump(), f)


def save_to_s3(config: InferenceJobConfig, local_path: Path, storage_path: str):
    s3 = s3fs.S3FileSystem()
    if storage_path.endswith("/"):
        storage_path = "s3://" + str(Path(storage_path[5:]) / config.name / "results.json")
    logger.info(f"Storing into {storage_path}...")
    s3.put_file(local_path, storage_path)


def save_outputs(config: InferenceJobConfig, results: JobOutput) -> Path:
    storage_path = config.job.storage_path

    # generate local temp file ANYWAY:
    # - if storage_path is not provided, it will be stored and kept into a default dir
    # - if storage_path is provided AND saving to S3 is successful, local file is deleted
    local_path = Path(Path.home() / ".lumigator" / "results" / config.name / "results.json")

    try:
        save_to_disk(local_path, results)

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
        output_model_name = config.inference_server.model
        model_client = LiteLLMModelClient(config)
    elif config.hf_pipeline:
        logger.info(f"Using HuggingFace client with model {config.hf_pipeline.model_name_or_path}.")
        model_client = HuggingFaceModelClient(config)
        output_model_name = config.hf_pipeline.model_name_or_path
    else:
        raise NotImplementedError("Inference pipeline not supported.")

    # We keep any columns that were already there (not just the original input
    # samples, but also past predictions under another column name)
    output.update(dataset.to_dict())

    # We are trusting the user: if the dataset already had a column with the output_field
    # they selected, we overwrite it with the values from our inference.

    if config.job.output_field in dataset.column_names:
        logger.warning(f"Overwriting {config.job.output_field}")

    predictions, inference_time = predict(dataset_iterable, model_client)
    predictions: list[PredictionResult] = predictions
    output[config.job.output_field] = [p.prediction for p in predictions]
    output["inference_metrics"] = [p.metrics for p in predictions]
    output["model"] = output_model_name
    output["inference_time"] = inference_time
    if all(p.metrics is not None for p in predictions):
        avg_prompt_tokens = sum([p.metrics.prompt_tokens for p in predictions]) / len(predictions)
        avg_total_tokens = sum([p.metrics.total_tokens for p in predictions]) / len(predictions)
        avg_completion_tokens = sum([p.metrics.completion_tokens for p in predictions]) / len(predictions)
        metrics = InferenceMetrics(
            prompt_tokens=avg_prompt_tokens,
            total_tokens=avg_total_tokens,
            completion_tokens=avg_completion_tokens,
        )
    else:
        metrics = None
    logger.info(output)

    results = JobOutput(
        metrics=metrics,
        parameters=config,
        artifacts=InferenceJobOutput.model_validate(output),
    )

    output_path = save_outputs(config, results)
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

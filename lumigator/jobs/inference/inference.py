"""python job to run batch inference"""

import argparse
import os
from pathlib import Path

import s3fs
from dataset import create_dataloader
from datasets import load_from_disk
from inference_config import InferenceJobConfig
from loguru import logger
from model_clients.base_client import BaseModelClient
from model_clients.external_api_clients import LiteLLMModelClient
from model_clients.huggingface_clients import HuggingFaceModelClientFactory
from torch.utils.data import DataLoader
from tqdm import tqdm
from utils import timer

from schemas import AverageInferenceMetrics, InferenceJobOutput, JobOutput, PredictionResult


@timer
def predict(dataloader: DataLoader, model_client: BaseModelClient) -> list[PredictionResult]:
    predictions = []

    for batch in dataloader:
        examples = batch["examples"]
        predictions.extend(model_client.predict(examples))

    return predictions


def save_to_disk(local_path: Path, results: JobOutput):
    logger.info(f"Storing into {local_path}...")
    local_path.parent.mkdir(exist_ok=True, parents=True)
    with local_path.open("w") as f:
        f.write(results.model_dump_json())


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


def run_inference(config: InferenceJobConfig, api_key: str | None = None) -> Path:
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

    # Create a torch DataLoader to manage the data in batches
    torch_dataloader = create_dataloader(dataset, config)

    # Enable / disable tqdm
    dataloader_iterable = tqdm(torch_dataloader, unit="batch") if config.job.enable_tqdm else torch_dataloader

    # Choose which model client to use
    if config.inference_server is not None:
        # a model *inference service* is passed
        output_model_name = config.inference_server.model
        model_client = LiteLLMModelClient(config, api_key)
    elif config.hf_pipeline:
        logger.info(f"Using HuggingFace client with model {config.hf_pipeline.model_name_or_path}.")
        model_client = HuggingFaceModelClientFactory.create(config, api_key)
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

    prediction_results: list[PredictionResult]
    inference_time: float
    prediction_results, inference_time = predict(dataloader_iterable, model_client)
    output[config.job.output_field] = [p.prediction for p in prediction_results]
    output["reasoning"] = [p.reasoning for p in prediction_results]
    output["inference_metrics"] = [p.metrics for p in prediction_results]
    output["model"] = output_model_name
    output["inference_time"] = inference_time

    artifacts = InferenceJobOutput.model_validate(output)

    all_metrics_present = all(p.metrics for p in prediction_results)

    if any(p.metrics for p in prediction_results) != all_metrics_present:
        raise ValueError("Prediction result 'metrics' must be present in ALL results or NONE, but not in SOME.")

    results = JobOutput(artifacts=artifacts, parameters=config)

    # Only attempt to metric calculate averages if we have a metric for EVERY prediction result.
    if all_metrics_present:
        total_results = len(prediction_results)
        avg_prompt_tokens = sum(p.metrics.prompt_tokens for p in prediction_results) / total_results
        avg_total_tokens = sum(p.metrics.total_tokens for p in prediction_results) / total_results
        avg_completion_tokens = sum(p.metrics.completion_tokens for p in prediction_results) / total_results
        avg_reasoning_tokens = sum(p.metrics.reasoning_tokens for p in prediction_results) / total_results
        avg_answer_tokens = sum(p.metrics.answer_tokens for p in prediction_results) / total_results

        metrics = AverageInferenceMetrics(
            avg_prompt_tokens=avg_prompt_tokens,
            avg_total_tokens=avg_total_tokens,
            avg_completion_tokens=avg_completion_tokens,
            avg_reasoning_tokens=avg_reasoning_tokens,
            avg_answer_tokens=avg_answer_tokens,
        )

        results.metrics = metrics

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
        # Attempt to retrieve the API key from the environment for use with the clients.
        api_key = os.environ.get("api_key")
        result_dataset_path = run_inference(config, api_key)
        logger.info(f"Inference results stored at {result_dataset_path}")

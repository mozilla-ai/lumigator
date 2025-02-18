import json
from pathlib import Path

import click
import s3fs
from datasets import load_from_disk
from eval_metrics import EvaluationMetrics
from loguru import logger
from utils import timer

from schemas import EvalJobArtifacts, EvalJobConfig, EvalJobMetrics, JobOutput


def save_to_disk(local_path: Path, data: JobOutput):
    logger.info(f"Storing evaluation results into {local_path}...")
    local_path.parent.mkdir(exist_ok=True, parents=True)
    with local_path.open("w") as f:
        json.dump(data.model_dump(), f)


def save_to_s3(config: EvalJobConfig, local_path: Path, storage_path: str):
    s3 = s3fs.S3FileSystem()
    if storage_path.endswith("/"):
        storage_path = "s3://" + str(Path(storage_path[5:]) / config.name / "results.json")
    logger.info(f"Storing evaluation results into {storage_path}...")
    s3.put_file(local_path, storage_path)


def save_outputs(config: EvalJobConfig, eval_results: JobOutput) -> Path:
    storage_path = config.evaluation.storage_path

    # generate local temp file ANYWAY:
    # - if storage_path is not provided, it will be stored and kept into a default dir
    # - if storage_path is provided AND saving to S3 is successful, local file is deleted
    local_path = Path(Path.home() / ".lumigator" / "results" / config.name / "results.json")

    try:
        save_to_disk(local_path, eval_results)

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


@timer
def run_eval_metrics(predictions: list, ground_truth: list, evaluation_metrics: list) -> EvalJobMetrics:
    em = EvaluationMetrics(evaluation_metrics)
    evaluation_results = em.run_all(predictions, ground_truth)
    return EvalJobMetrics.model_validate(evaluation_results)


def run_eval(config: EvalJobConfig) -> Path:
    max_samples = config.evaluation.max_samples

    # Load dataset given its URI
    dataset = load_from_disk(config.dataset.path)
    logger.info(f"Retrieving {config.dataset.path} for evaluation")

    # Limit dataset length if max_samples is specified
    if max_samples < 1 or max_samples > len(dataset):
        logger.info(f"max_samples ({max_samples}) resized to dataset size ({len(dataset)})")
        max_samples = len(dataset)
    dataset = dataset.select(range(max_samples))

    logger.info(dataset)

    metric_results, evaluation_time = run_eval_metrics(
        dataset["predictions"], dataset["ground_truth"], config.evaluation.metrics
    )

    # add input data to results dict
    if config.evaluation.return_input_data:
        artifacts = EvalJobArtifacts(
            predictions=dataset["predictions"], ground_truth=dataset["ground_truth"], evaluation_time=evaluation_time
        )
    else:
        artifacts = None
    evaluation_results = JobOutput(
        metrics=metric_results,
        parameters=config,
        artifacts=artifacts,
    )
    output_path = save_outputs(config, evaluation_results)
    return output_path


@click.command()
@click.option("--config")
def eval_command(config: str) -> None:
    config_dict = json.loads(config)
    logger.info(f"{config_dict}")
    config_model = EvalJobConfig(**config_dict)
    run_eval(config_model)


if __name__ == "__main__":
    logger.info("Starting evaluation job...")
    eval_command()

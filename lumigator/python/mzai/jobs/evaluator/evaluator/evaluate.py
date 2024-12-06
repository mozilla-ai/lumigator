import json
from pathlib import Path

import click
import s3fs
from datasets import load_from_disk
from eval_lite_config import EvalJobConfig
from eval_metrics import EvaluationMetrics
from loguru import logger


def save_to_disk(local_path: Path, data_dict: dict):
    logger.info(f"Storing into {local_path}...")
    local_path.parent.mkdir(exist_ok=True, parents=True)
    with local_path.open("w") as f:
        json.dump(data_dict, f)


def save_to_s3(config: dict, local_path: Path, storage_path: str):
    s3 = s3fs.S3FileSystem()
    if storage_path.endswith("/"):
        storage_path = "s3://" + str(
            Path(storage_path[5:]) / config.get("name") / "eval_results.json"
        )
    logger.info(f"Storing into {storage_path}...")
    s3.put_file(local_path, storage_path)


def save_outputs(config: dict, eval_results: dict) -> Path:
    storage_path = config.get("evaluation").get("storage_path")

    local_path = Path("eval_results.json")

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


def run_eval_metrics(predictions: list, ground_truth: list, evaluation_metrics: list):
    em = EvaluationMetrics(evaluation_metrics)
    evaluation_results = em.run_all(predictions, ground_truth)

    return evaluation_results


def run_eval(config: EvalJobConfig) -> Path:
    max_samples = config.evaluation.max_samples

    # Load dataset given its URI
    dataset = load_from_disk(config.dataset.path)
    if max_samples:
        logger.info(f"max_samples ({max_samples}) resized to dataset size ({len(dataset)})")
        # select data between the minimum and total length of dataset
        num_samples = range(min(max_samples, len(dataset)))
        dataset = dataset.select(num_samples)

    # run evaluation and append to results dict
    predictions = dataset["predictions"]
    ground_truth = dataset["ground_truth"]

    evaluation_results = run_eval_metrics(predictions, ground_truth, config.evaluation.metrics)

    # add input data to results dict
    if config.evaluation.return_input_data:
        evaluation_results["predictions"] = dataset["predictions"]
        evaluation_results["ground_truth"] = dataset["ground_truth"]

    output_path = save_outputs(config, evaluation_results)
    return output_path


@click.command()
@click.option("--config")
def eval_command(config: str) -> None:
    config_dict = json.loads(config)
    logger.info(f"{config_dict}")
    run_eval(config_dict)


if __name__ == "__main__":
    logger.info("Starting evaluation job...")
    eval_command()

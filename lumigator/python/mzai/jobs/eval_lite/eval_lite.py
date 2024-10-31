import json
from pathlib import Path

import click
import numpy as np
import s3fs
from datasets import load_from_disk
from loguru import logger
import evaluate

class EvaluationMetrics:
    def __init__(self, metrics):
        self._supported_metrics = {
            "rouge": self._rouge,
            "meteor": self._meteor,
            "bertscore": self._bertscore,
        }

        # chosen metrics are the intersection between the provided and the supported ones
        self._chosen_metrics = set(metrics) & set(self._supported_metrics.keys())
        # unsupported metrics are the difference between the provided and the supporterd ones
        self._unsupported_metrics = set(metrics) - set(self._supported_metrics.keys())

        if len(self._chosen_metrics) == 0:
            logger.info("No valid metrics selected")
        else:
            logger.info(f"Chosen metrics: {self._chosen_metrics}")

        if len(self._unsupported_metrics) > 0:
            logger.info(f"Unsupported metrics: {self._unsupported_metrics}")

    def _rouge(self, pred, ref):
        ev = evaluate.load("rouge")

        # compute with use_aggregator = False to get individual scores
        evals = ev.compute(predictions=pred, references=ref, use_aggregator=False)

        # calculate mean for each of the submetrics (rouge1, rouge2, rougeL, rougeLsum)
        for k in ["rouge1", "rouge2", "rougeL", "rougeLsum"]:
            evals[f"{k}_mean"] = np.mean(evals[k])

        return evals

    def _meteor(self, pred, ref):
        ev = evaluate.load("meteor")

        # initialize dictionary with metric name
        evals = {"meteor": []}

        # run sample-wise evals (as default implementation only returns mean value)
        for p, r in zip(pred, ref):
            evals["meteor"].append(ev.compute(predictions=[p], references=[r])["meteor"])

        # calculate mean
        evals["meteor_mean"] = np.mean(evals["meteor"])

        return evals

    def _bertscore(self, pred, ref):
        ev = evaluate.load("bertscore")

        # calculate evals (the default is not to aggregate them)
        evals = ev.compute(predictions=pred, references=ref, lang="en")

        # calculate mean for each of the submetrics (precision, recall, f1)
        for k in ["precision", "recall", "f1"]:
            evals[f"{k}_mean"] = np.mean(evals[k])

        return evals

    def run_all(self, pred, ref):
        results = {}

        for metric in self._chosen_metrics:
            results[metric] = self._supported_metrics[metric](pred, ref)

        return results



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

    local_path = Path( "eval_results.json")

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
def run_eval(config: dict) -> Path:

    max_samples = config.get("max_samples")

    # Load dataset given its URI
    dataset = load_from_disk(config.get("dataset").get("path"))
    if max_samples:
        logger.info(f"max_samples ({max_samples}) resized to dataset size ({len(dataset)})")
        # select data between the minimum and total length of dataset
        num_samples = range(min(max_samples, len(dataset)))
        dataset = dataset.select(num_samples)

    # run evaluation and append to dict
    predictions = dataset["predictions"]
    ground_truth = dataset["ground_truth"]

    evaluation_results = run_eval_metrics(
        predictions, ground_truth, config.get("evaluation").get("metrics")
    )

    # add input data to results dict
    if config.get("evaluation").get("return_input_data"):
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
    logger.info("starting..")
    eval_command()

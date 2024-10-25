"""python job to run eval inference"""

import argparse
import json
from collections.abc import Iterable
from pathlib import Path

import s3fs
from box import Box
from datasets import load_from_disk
from loguru import logger
from tqdm import tqdm

class EvaluationMetrics:
    def __init__(self, metrics):
        self._supported_metrics = {
            "rouge": self._rouge,
            "meteor": self._meteor,
            "bertscore": self._bertscore,
        }

        # chosen metrics are the intersection between the provided and the supporterd ones
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


def save_to_s3(config: Box, local_path: Path, storage_path: str):
    s3 = s3fs.S3FileSystem()
    if storage_path.endswith("/"):
        storage_path = "s3://" + str(
            Path(storage_path[5:]) / config.name / "inference_results.json"
        )
    logger.info(f"Storing into {storage_path}...")
    s3.put_file(local_path, storage_path)


def save_outputs(config: dict, inference_results: dict) -> Path:
    storage_path = config.evaluation.storage_path

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
def evaluate(predictions: list, ground_truth: list, evaluation_metrics: list):
    em = EvaluationMetrics(evaluation_metrics)
    evaluation_results = em.run_all(predictions, ground_truth)

    return evaluation_results
def run_eval(config) -> Path:
    # Load dataset given its URI
    dataset = load_from_disk(config.dataset.path)

    # Limit dataset length if max_samples is specified
    max_samples = config.evaluation.max_samples
    if max_samples and max_samples > 0:
        if max_samples > len(dataset):
            logger.info(f"max_samples ({max_samples}) resized to dataset size ({len(dataset)})")
            max_samples = len(dataset)
        dataset = dataset.select(range(max_samples))

    # Enable / disable tqdm
    input_samples = dataset["examples"]
    dataset_iterable = tqdm(input_samples) if config.evaluation.enable_tqdm else input_samples


    ground_truth = dataset["ground_truth"]
        evaluation_results, evaluation_time = evaluate(
            dataset_iterable, ground_truth, config.evaluation.metrics
        )

        # add timing to results dict
        evaluation_results["evaluation_time"] = evaluation_time

        # add predictions to results dict
        if config.evaluation.return_predictions:
            evaluation_results["predictions"] = predictions

        # add model name to results dict
        evaluation_results["model"] = output_model_name

        output_path = save_outputs(config, evaluation_results)
        return output_path

@click.group(name="Evaluator CLI", help="Entrypoints for the evaluator CLI ")
def cli():
    pass

@click.group(name="evaluate", help="Run an evaluation job.")
def group() -> None:
    pass

cli.add_command(group)

@group.command("lm-harness", help="Run the lm-harness evaluation job.")
@click.option("--config", type=str)
def lm_harness_command(config: str) -> None:
    config = parse_config_option(config)
    run_eval(config)


if __name__ == "__main__":
    cli()

import evaluate
import numpy as np
from loguru import logger


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

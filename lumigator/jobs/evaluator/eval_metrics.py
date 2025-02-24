import functools
import json
from enum import Enum
from pathlib import Path

import evaluate
import numpy as np
from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCase, LLMTestCaseParams
from loguru import logger

from schemas import EvalJobMetrics

G_EVAL_PROMPTS = "g_eval_prompts.json"
MEASURE_RETRIES = 3


class EvaluationFields(Enum):
    """Defines the fields a given metric might require as inputs."""

    PREDICTION = "pred"
    GROUND_TRUTH = "ref"
    LLM_INPUT = "example"


class EvaluationMetrics:
    def __init__(self, metrics):
        # for each of the supported metrics, we provide a dictionary specifying
        # which method implements it and which fields it requires (only the original
        # LLM input and the reference / ground truth are specified, as predictions
        # are always passed for evaluation).
        self._supported_metrics = {
            "rouge": {"method": self._rouge, "requires": [EvaluationFields.GROUND_TRUTH]},
            "meteor": {"method": self._meteor, "requires": [EvaluationFields.GROUND_TRUTH]},
            "bertscore": {"method": self._bertscore, "requires": [EvaluationFields.GROUND_TRUTH]},
            "bleu": {"method": self._bleu, "requires": [EvaluationFields.GROUND_TRUTH]},
            "g_eval_summarization": {
                # the available tasks in g_eval are the ones we have defined
                # criteria / evaluation steps for inside `g_eval_prompts.json`
                "method": functools.partial(self._g_eval, task="summarization"),
                "requires": [EvaluationFields.GROUND_TRUTH, EvaluationFields.LLM_INPUT],
            },
        }

        # chosen metrics are the intersection between the provided and the supported ones
        self._chosen_metrics = set(metrics) & set(self._supported_metrics.keys())
        # unsupported metrics are the difference between the provided and the supported ones
        self._unsupported_metrics = set(metrics) - set(self._supported_metrics.keys())

        if len(self._chosen_metrics) == 0:
            logger.info("No valid metrics selected")
        else:
            logger.info(f"Chosen metrics: {self._chosen_metrics}")

        if len(self._unsupported_metrics) > 0:
            logger.warning(f"Unsupported metrics: {self._unsupported_metrics}")

    def _rouge(self, pred: list, ref: list):
        ev = evaluate.load("rouge")

        # compute with use_aggregator = False to get individual scores
        evals = ev.compute(predictions=pred, references=ref, use_aggregator=False)

        # calculate mean for each of the submetrics (rouge1, rouge2, rougeL, rougeLsum)
        for k in ["rouge1", "rouge2", "rougeL", "rougeLsum"]:
            evals[f"{k}_mean"] = np.mean(evals[k])

        return evals

    def _meteor(self, pred: list, ref: list):
        ev = evaluate.load("meteor")

        # initialize dictionary with metric name
        evals = {"meteor": []}

        # run sample-wise evals (as default implementation only returns mean value)
        for p, r in zip(pred, ref):
            evals["meteor"].append(ev.compute(predictions=[p], references=[r])["meteor"])

        # calculate mean
        evals["meteor_mean"] = np.mean(evals["meteor"])

        return evals

    def _bleu(self, pred, ref):
        ev = evaluate.load("bleu")

        # initialize dictionary with metric name
        evals = {"bleu": []}

        # run sample-wise evals
        for p, r in zip(pred, ref):
            # assumption that there is only one reference per prediction
            # TODO: check how to support multiple references
            result = ev.compute(predictions=[p], references=[[r]])
            evals["bleu"].append(result["bleu"])

        # calculate mean
        evals["bleu_mean"] = np.mean(evals["bleu"])

        return evals

    def _bertscore(self, pred: list, ref: list):
        """https://huggingface.co/spaces/evaluate-metric/bertscore
        BERTScore leverages the pre-trained contextual embeddings from BERT
        and matches words in candidate and reference sentences by cosine similarity.

        It uses two lists of strings of type Any (in our case, mostly strings) for comparison

        predictions = ["hello world", "general kenobi"]
        references = ["goodnight moon", "the sun is shining"]
        results = bertscore.compute(predictions=predictions)
        """
        ev = evaluate.load("bertscore")

        # calculate evals (the default is not to aggregate them)
        evals = ev.compute(predictions=pred, references=ref, lang="en")

        # calculate mean for each of the submetrics (precision, recall, f1)
        for k in ["precision", "recall", "f1"]:
            evals[f"{k}_mean"] = np.mean(evals[k])

        return evals

    def _g_eval_measure_with_retry(self, metric, test_case, max_retries=3):
        """Calls metric.measure with retry logic and returns the score and reason.

        Args:
            metric: The metric object with measure method and score/reason properties
            test_case: The test case to measure
            max_retries: Maximum number of retry attempts

        Returns:
            dict: Dictionary with score and reason

        Raises:
            ValueError: If all retry attempts fail
        """
        for attempt in range(1, max_retries + 1):
            try:
                metric.measure(test_case)
                return {"score": metric.score, "reason": metric.reason}
            except ValueError as e:
                logger.warning(f"Attempt {attempt}/{max_retries} failed: {str(e)}")
                if attempt == max_retries:
                    raise e

        raise ValueError("All retry attempts failed")

    def _g_eval(self, llm_inputs: list, pred: list, ref: list, task: str) -> dict:
        """Runs the deepeval implementation of the G-Eval LLM-as-judge evaluation.

        The GEval class takes some evaluation criteria or steps provided as prompts
        to an LLM and applies them to evaluate a given model's predictions given
        the original inputs and expected outputs (ground truth). The default
        implementation uses GPT4, but can be adapted to support any other model.

        See: https://github.com/nlpyang/geval (G-Eval)
        See: https://docs.confident-ai.com/docs/metrics-llm-evals (deepeval)
        """
        # Load task-dependent criteria / evaluation steps
        with Path(G_EVAL_PROMPTS).open() as f:
            prompt_templates = json.load(f)

        evals = {}
        for metric_name in prompt_templates[task]:
            metric = GEval(
                name=metric_name,
                # NOTE: deepeval allows you to provide either criteria or evaluation_steps, and not both.
                #       In this first iteration we pick evaluation_steps
                evaluation_steps=prompt_templates[task][metric_name]["evaluation_steps"],
                evaluation_params=[
                    LLMTestCaseParams.INPUT,
                    LLMTestCaseParams.ACTUAL_OUTPUT,
                    LLMTestCaseParams.EXPECTED_OUTPUT,
                ],
            )

            evals_for_metric = []
            # iterate on all samples
            for p, r, e in zip(pred, ref, llm_inputs):
                test_case = LLMTestCase(input=e, expected_output=r, actual_output=p)

                try:
                    result = self._g_eval_measure_with_retry(metric, test_case, max_retries=MEASURE_RETRIES)
                    evals_for_metric.append(result)
                except ValueError as e:
                    # Handle the failure case
                    logger.error(f"G-Eval measurement failed after {MEASURE_RETRIES} attempts: {e}")
                    raise e

            evals[metric_name] = evals_for_metric
            evals[f"{metric_name}_mean"] = np.mean([x["score"] for x in evals_for_metric])

        return evals

    def run_all(self, llm_inputs: list, pred: list, ref: list) -> EvalJobMetrics:
        results = {}

        for metric in self._chosen_metrics:
            if EvaluationFields.LLM_INPUT in self._supported_metrics[metric]["requires"]:
                results[metric] = self._supported_metrics[metric]["method"](llm_inputs, pred, ref)
            else:
                results[metric] = self._supported_metrics[metric]["method"](pred, ref)

        return EvalJobMetrics(**results)

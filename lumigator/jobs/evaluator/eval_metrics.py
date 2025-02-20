from enum import Enum

import evaluate
import numpy as np
from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCase, LLMTestCaseParams
from loguru import logger

from schemas import EvalJobMetrics


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
            "g_eval_consistency": {
                "method": self._g_eval_consistency,
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

        It uses two lists of strings of type Any (in our case, mostly strings) for comparsion

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

    def _g_eval_consistency(self, llm_inputs: list, pred: list, ref: list) -> dict:
        correctness_metric = GEval(
            name="Consistency",
            # # NOTE: you can only provide either criteria or evaluation_steps, and not both
            # criteria="The factual alignment between the summary and the summarized source. "
            # "A factually consistent summary contains only statements that are entailed by the source document. "
            # "Annotators were also asked to penalize summaries that contained hallucinated facts.",
            evaluation_steps=[
                "Read the source document carefully and identify the main facts and details it presents",
                "Read the summary and compare it to the source document."
                "Check if the summary contains any factual errors that are not supported by the source document",
                "Assign a score for consistency based on the Evaluation Criteria",
            ],
            evaluation_params=[
                LLMTestCaseParams.INPUT,
                LLMTestCaseParams.ACTUAL_OUTPUT,
                LLMTestCaseParams.EXPECTED_OUTPUT,
            ],
        )

        # initialize dictionary with metric name
        evals = {"consistency": []}

        # run sample-wise evals (as default implementation only returns mean value)
        for p, r, e in zip(pred, ref, llm_inputs):
            test_case = LLMTestCase(input=e, expected_output=r, actual_output=p)
            try:
                correctness_metric.measure(test_case)
            except ValueError as e:
                logger.error(f"Caught ValueError: {e}")
            evals["consistency"].append({"score": correctness_metric.score, "reason": correctness_metric.reason})

        evals["consistency_mean"] = np.mean([x["score"] for x in evals["consistency"]])

        return evals

    def run_all(self, llm_inputs: list, pred: list, ref: list) -> EvalJobMetrics:
        results = {}

        for metric in self._chosen_metrics:
            if EvaluationFields.LLM_INPUT in self._supported_metrics[metric]["requires"]:
                results[metric] = self._supported_metrics[metric]["method"](llm_inputs, pred, ref)
            else:
                results[metric] = self._supported_metrics[metric]["method"](pred, ref)

        return EvalJobMetrics(**results)

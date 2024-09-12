"""
lm-buddy entrypoint to run evaluations using a Prometheus inference server
see https://github.com/kaistAI/prometheus/blob/main/evaluation/benchmark/run_absolute_scoring.py
"""

import copy
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from datasets import Dataset
from loguru import logger
from openai import OpenAI, OpenAIError
from openai.types import Completion
from tqdm import tqdm

from lm_buddy.configs.huggingface import AutoTokenizerConfig
from lm_buddy.configs.jobs.prometheus import PrometheusJobConfig
from lm_buddy.constants import LM_BUDDY_RESULTS_PATH
from lm_buddy.jobs.asset_loader import (
    HuggingFaceDatasetLoader,
    HuggingFaceModelLoader,
    HuggingFaceTokenizerLoader,
)
from lm_buddy.jobs.common import EvaluationResult
from lm_buddy.jobs.evaluation.conversation import get_conv_template
from lm_buddy.preprocessing import format_dataset_with_prompt
from lm_buddy.tracking.artifact_utils import (
    ArtifactType,
    build_directory_artifact,
    default_artifact_name,
)


@dataclass
class BadResponseError(Exception):
    def __init__(self, message, error=None):
        self.message = message
        self.error = error


def openai_completion(
    config: PrometheusJobConfig, client: OpenAI, engine: str, prompt: str
) -> Completion:
    """Connects to a remote OpenAI-API-compatible Prometheus endpoint
    and returns a Completion holding the model's response.
    """

    return client.completions.create(
        model=engine,
        prompt=prompt,
        best_of=config.prometheus.best_of,
        max_tokens=config.prometheus.max_tokens,
        frequency_penalty=config.prometheus.frequency_penalty,
        temperature=config.prometheus.temperature,
        top_p=config.prometheus.top_p,
    )


def parse_response(config: PrometheusJobConfig, response: Completion) -> tuple[str, str]:
    """Given a Prometheus eval response as returned by the OpenAI API
    endpoint (i.e. in Completion format), extract feedback and score.
    """

    if response is None:
        raise BadResponseError("Server returned an empty response")

    try:
        response_text = response.choices[0].text
        # note: this can raise a ValueError if the message is malformed
        feedback, score = response_text.split("[RESULT]")
        feedback = feedback.strip()
        score = score.strip()
        if score not in [str(s) for s in config.evaluation.scores]:
            raise BadResponseError(f"Score {score} is not in range")
    except (ValueError, BadResponseError) as e:
        raise BadResponseError(f"Server returned a malformed response ({e})", e)

    return feedback, score


def instruction_to_prompt(config: PrometheusJobConfig, instruction: str) -> str:
    """Given some text containing Prometheus instructions, a conversation
    template (e.g. "llama-2") and a system message (e.g. "You are a
    fair evaluator language model"), generate an actual prompt.
    """
    conv = get_conv_template(config.evaluation.conversation_template)
    conv.set_system_message(config.evaluation.conversation_system_message)
    conv.append_message(conv.roles[0], instruction)
    conv.append_message(conv.roles[1], None)
    return conv.get_prompt()


def get_response_with_retries(
    config: PrometheusJobConfig,
    client: OpenAI,
    engine: str,
    prompt: str,
) -> tuple[str, str]:
    current_retry_attempt = 1
    while current_retry_attempt <= config.evaluation.max_retries:
        try:
            response = openai_completion(config, client, engine, prompt)
            feedback, score = parse_response(config, response)
            break
        except (OpenAIError, BadResponseError) as e:
            logger.warning(
                f"{e.message}: "
                f"Retrying ({current_retry_attempt}/{config.evaluation.max_retries})"
            )
            current_retry_attempt += 1
            if current_retry_attempt > config.evaluation.max_retries:
                raise e
    return (feedback, score)


def run_eval(config: PrometheusJobConfig) -> Path:
    # Resolve the engine model
    hf_model_loader = HuggingFaceModelLoader()
    engine_path = hf_model_loader.resolve_asset_path(config.prometheus.inference.engine)

    # Load dataset from W&B artifact
    hf_dataset_loader = HuggingFaceDatasetLoader()
    dataset = hf_dataset_loader.load_dataset(config.dataset)
    if config.dataset.prompt_template is not None:
        dataset = format_dataset_with_prompt(
            dataset, config.dataset.prompt_template, config.dataset.text_field
        )

    # Get the tokenizer
    hf_tok_loader = HuggingFaceTokenizerLoader()
    tokenizer_config = AutoTokenizerConfig(path=config.prometheus.inference.engine)
    tokenizer = hf_tok_loader.load_pretrained_tokenizer(tokenizer_config)

    # Enable / disable tqdm
    dataset_iterable = tqdm(dataset) if config.evaluation.enable_tqdm else dataset

    # Generator that iterates over samples and yields new rows with the prometheus outputs
    def data_generator():
        # Instantiate OpenAI client to speak with the vLLM endpoint
        # Client is non-serializable so must be instantiated internal to this method
        # Reference: https://huggingface.co/docs/datasets/en/troubleshoot#pickling-issues
        client = OpenAI(base_url=config.prometheus.inference.base_url)

        for sample in dataset_iterable:
            # convert instructions from the dataset (`text_field` in a dict) to
            # prompts that prometheus accepts
            prompt = instruction_to_prompt(config, sample[config.dataset.text_field])

            # skip those examples which are too long
            tokenized_prompt = tokenizer(prompt, truncation=False)
            if len(tokenized_prompt["input_ids"]) > 3072:
                logger.warning(f"Skipping row due to prompt exceeding token limit: {prompt=}")
                continue

            # prepare output
            result: dict[str, Any] = copy.deepcopy(sample)
            result["prometheus_output"] = []
            result["prometheus_score"] = []

            for _ in range(config.evaluation.num_answers):
                (feedback, score) = get_response_with_retries(config, client, engine_path, prompt)
                result["prometheus_output"].append(feedback)
                result["prometheus_score"].append(score)

            yield result

    result_dataset = Dataset.from_generator(data_generator)

    # Save dataset to disk
    storage_path = config.evaluation.storage_path or LM_BUDDY_RESULTS_PATH
    result_dataset_path = Path(storage_path) / config.name / "prometheus"
    result_dataset.save_to_disk(str(result_dataset_path))

    return result_dataset_path


def run_prometheus(config: PrometheusJobConfig) -> EvaluationResult:
    # Run eval and store output in local filename
    result_dataset_path = run_eval(config)
    logger.info(f"Prometheus evaluation dataset stored at {result_dataset_path}")

    # Create a directory artifact for the HF dataset
    artifact_name = default_artifact_name(config.name, artifact_type=ArtifactType.DATASET)
    dataset_artifact = build_directory_artifact(
        artifact_name=artifact_name,
        artifact_type=ArtifactType.DATASET,
        dir_path=result_dataset_path,
        reference=False,
    )

    return EvaluationResult(
        artifacts=[dataset_artifact],
        dataset_path=result_dataset_path,
        tables={},
    )

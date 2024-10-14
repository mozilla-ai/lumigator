"""entrypoint to perform batch inference"""

import json
from collections.abc import Iterable
from pathlib import Path

import s3fs
from loguru import logger
from tqdm import tqdm

from evaluator.configs.jobs.inference import InferenceJobConfig
from evaluator.configs.vllm import VLLMCompletionsConfig
from evaluator.constants import EVALUATOR_RESULTS_PATH
from evaluator.jobs.asset_loader import (
    HuggingFaceDatasetLoader,
    HuggingFaceModelLoader,
)
from evaluator.jobs.common import EvaluationResult
from evaluator.jobs.model_clients import (
    BaseModelClient,
    HuggingFaceModelClient,
    MistralModelClient,
    OpenAIModelClient,
    SummarizationPipelineModelClient,
)
from evaluator.jobs.utils import timer


@timer
def predict(dataset_iterable: Iterable, model_client: BaseModelClient) -> list:
    predictions = []

    for sample_txt in dataset_iterable:
        predictions.append(model_client.predict(sample_txt))

    return predictions


def save_outputs(config: InferenceJobConfig, evaluation_results: dict) -> Path:
    storage_path = config.inference.storage_path

    def save_to_disk(local_path: Path):
        logger.info(f"Storing into {local_path}...")
        local_path.parent.mkdir(exist_ok=True, parents=True)
        with local_path.open("w") as f:
            json.dump(evaluation_results, f)

    def save_to_s3(local_path: Path, storage_path: str):
        s3 = s3fs.S3FileSystem()
        if storage_path.endswith("/"):
            storage_path = "s3://" + str(Path(storage_path[5:]) / config.name / "eval_results.json")
        logger.info(f"Storing into {storage_path}...")
        s3.put_file(local_path, storage_path)

    # generate local temp file ANYWAY
    # (we don't want to lose all eval data if there is an issue wth s3)
    local_path = Path(EVALUATOR_RESULTS_PATH) / config.name / "eval_results.json"

    try:
        save_to_disk(local_path)

        # copy to s3 and return path
        if storage_path is not None and storage_path.startswith("s3://"):
            save_to_s3(local_path, storage_path)
            return storage_path

        return local_path

    except Exception as e:
        logger.error(e)


def inference(config: InferenceJobConfig) -> Path:
    # Init loaders
    hf_dataset_loader = HuggingFaceDatasetLoader()
    hf_model_loader = HuggingFaceModelLoader()

    # Load dataset given its URI
    dataset = hf_dataset_loader.load_dataset(config.dataset)

    # Limit dataset length if max_samples is specified
    max_samples = config.inference.max_samples
    if max_samples and max_samples > 0:
        if max_samples > len(dataset):
            logger.info(f"max_samples ({max_samples}) resized to dataset size ({len(dataset)})")
            max_samples = len(dataset)
        dataset = dataset.select(range(max_samples))

    # Enable / disable tqdm
    input_samples = dataset["examples"]
    dataset_iterable = tqdm(input_samples) if config.inference.enable_tqdm else input_samples

    # Choose which model client to use
    if isinstance(config.model, VLLMCompletionsConfig):
        model_name = config.model.inference.base_url
        output_model_name = config.model.inference.engine
        if "mistral" in model_name:
            # run the mistral client
            logger.info(f"Using Mistral client. Endpoint: {model_name}")
            model_client = MistralModelClient(model_name, config.model)
        else:
            # run the openai client
            logger.info(f"Using OAI client. Endpoint: {model_name}")
            model_client = OpenAIModelClient(model_name, config.model)
    else:
        model_name = hf_model_loader.resolve_asset_path(config.model.path)
        output_model_name = config.model.path
        # depending on config, use the summarizer pipeline or directly call the model
        # for inference
        if config.inference.use_pipeline:
            logger.info(f"Using summarization pipeline. Model: {model_name}")
            model_client = SummarizationPipelineModelClient(model_name, config)
        else:
            logger.info(f"Using direct HF model invocation. Model: {model_name}")
            model_client = HuggingFaceModelClient(model_name, config)

    # run inference
    predictions, inference_time = predict(dataset_iterable, model_client)

    inference_dict = {}
    inference_dict["examples"] = dataset["examples"]
    inference_dict["predictions"] = predictions
    inference_dict["inference_time"] = inference_time

    # add model name to results dict
    inference_dict["model"] = output_model_name

    output_path = save_outputs(config, inference_dict)
    return output_path


def run_inference(config: InferenceJobConfig) -> EvaluationResult:
    # Run eval and store output in local filename
    result_dataset_path = inference(config)
    logger.info(f"Inference results stored at {result_dataset_path}")

    # TODO: we can probably remove returned values from this and other
    # jobs as we are not using them at all
    return EvaluationResult(
        artifacts=[],
        dataset_path=result_dataset_path,
        tables={},
    )
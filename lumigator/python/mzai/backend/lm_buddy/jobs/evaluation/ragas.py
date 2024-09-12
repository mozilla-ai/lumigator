from pathlib import Path

from datasets import Dataset
from langchain_community.embeddings.huggingface import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI
from loguru import logger
from ragas import evaluate as ragas_evaluate
from ragas.metrics import answer_relevancy, context_precision, context_recall, faithfulness

from lm_buddy.configs.jobs.ragas import RagasJobConfig
from lm_buddy.constants import LM_BUDDY_RESULTS_PATH
from lm_buddy.jobs.asset_loader import HuggingFaceDatasetLoader, HuggingFaceModelLoader
from lm_buddy.jobs.common import EvaluationResult
from lm_buddy.preprocessing import format_dataset_with_prompt
from lm_buddy.tracking.artifact_utils import (
    ArtifactType,
    build_directory_artifact,
    default_artifact_name,
)

RAGAS_METRICS_MAP = {
    "faithfulness": faithfulness,
    "answer_relevancy": answer_relevancy,
    "context_recall": context_recall,
    "context_precision": context_precision,
}


def run_eval(config: RagasJobConfig) -> Path:
    # load dataset from W&B artifact
    hf_dataset_loader = HuggingFaceDatasetLoader()
    evaluation_dataset = hf_dataset_loader.load_dataset(config.dataset)
    if config.dataset.prompt_template is not None:
        evaluation_dataset = format_dataset_with_prompt(
            evaluation_dataset, config.dataset.prompt_template, config.dataset.text_field
        )

    # Ragas custom model args
    ragas_args = {}

    # Load embedding model
    hf_model_loader = HuggingFaceModelLoader()
    embedding_model = hf_model_loader.resolve_asset_path(config.evaluation.embedding_model)
    ragas_args["embeddings"] = HuggingFaceEmbeddings(model_name=embedding_model)

    # Configure ragas to point to vllm instance for generation
    inference_engine = hf_model_loader.resolve_asset_path(config.judge.inference.engine)
    ragas_args["llm"] = ChatOpenAI(
        model=inference_engine,
        openai_api_key="EMPTY",  # needed to hit custom openai endpoint
        openai_api_base=config.judge.inference.base_url,
        max_tokens=config.judge.max_tokens,
        temperature=config.judge.temperature,
        top_k=config.judge.top_k,
    )

    ragas_metrics = [RAGAS_METRICS_MAP[metric] for metric in config.evaluation.metrics]
    result = ragas_evaluate(dataset=evaluation_dataset, metrics=ragas_metrics, **ragas_args)

    # Return a new dataset with score concatenated
    result_dataset = Dataset.from_pandas(result.to_pandas())

    # Save dataset to disk
    storage_path = config.evaluation.storage_path or LM_BUDDY_RESULTS_PATH
    result_dataset_path = Path(storage_path) / config.name / "ragas"
    result_dataset.save_to_disk(result_dataset_path)

    return result_dataset_path


def run_ragas(config: RagasJobConfig) -> EvaluationResult:
    # Run evaluation
    result_dataset_path = run_eval(config)
    logger.info(f"Ragas evaluation dataset stored at {result_dataset_path}")

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

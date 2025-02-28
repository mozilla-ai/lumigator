from collections import defaultdict
from time import sleep

import pandas as pd
import requests
from lumigator_schemas.experiments import GetExperimentResponse
from lumigator_schemas.workflows import WorkflowStatus
from lumigator_sdk.lumigator import LumigatorClient


def wait_for_all_workflows(lumi_client_int: LumigatorClient, experiment_id: str) -> GetExperimentResponse:
    """Wait for an experiment to complete."""
    still_running = True
    while still_running:
        still_running = False
        experiment_details = lumi_client_int.experiments.get_experiment(experiment_id)
        still_running_workflows = []
        for workflow in experiment_details.workflows:
            if workflow.status not in [WorkflowStatus.SUCCEEDED, WorkflowStatus.FAILED]:
                still_running_workflows.append(workflow.name)
        if still_running_workflows:
            still_running = True
            sleep(10)
    return experiment_details


def create_evaluation_config(
    model_name,
    ip_address,
    port=8000,
    custom_desc=None,
    provider="openai",
):
    # Handle name and model fields based on deployment type

    config = {
        "name": model_name,
        "model": model_name,
        "provider": provider,
    }

    # Set description
    if custom_desc:
        config["description"] = custom_desc
    else:
        config["description"] = f"The  deployment of {model_name}"

    config["base_url"] = f"http://{ip_address}:{port}/v1"

    return config


# Sort for readability - order by model architecture and size
def extract_size(model_name):
    if "70B" in model_name:
        return 70
    elif "32B" in model_name:
        return 32
    elif "14B" in model_name:
        return 14
    elif "8B" in model_name:
        return 8
    elif "7B" in model_name:
        return 7
    elif "1.5B" in model_name:
        return 1.5
    else:
        return 0


def extract_arch(model_name):
    if "Llama" in model_name:
        return "Llama"
    elif "Qwen" in model_name:
        return "Qwen"
    else:
        return "Other"


def compile_and_display_results(client: LumigatorClient, experiment: GetExperimentResponse):
    workflow_details = {}
    for workflow in experiment.workflows:
        if workflow.status == WorkflowStatus.SUCCEEDED:
            response = requests.get(workflow.artifacts_download_url)
            result = response.json()
            workflow_details[workflow.name] = result
        else:
            print(f"Workflow {workflow.id} failed: deleting the workflow.")
            client.workflows.delete_workflow(workflow.id)
    # First, let's deduplicate and organize the results
    model_results = defaultdict(dict)

    # Process results and remove duplicates
    for workflow in experiment.workflows:
        model_name = workflow.name
        for metric, value in workflow.metrics.items():
            if "token" in metric:
                model_results[model_name][metric] = round(value)
            else:
                model_results[model_name][metric] = value * 100

    # Convert to DataFrame for better visualization
    results_df = pd.DataFrame.from_dict(model_results, orient="index")

    # Add columns for sorting
    results_df["size"] = results_df.index.map(extract_size)
    results_df["architecture"] = results_df.index.map(extract_arch)

    # Sort by architecture and then by descending size
    results_df = results_df.sort_values(by=["fluency_mean"], ascending=[False])

    # Select just the most relevant metrics for display
    display_metrics = [
        "ref_token_length_mean",
        "avg_reasoning_tokens",
        "pred_token_length_mean",
        "rouge1_mean",
        "rouge2_mean",
        "rougeL_mean",
        "coherence_mean",
        "fluency_mean",
        "relevance_mean",
    ]
    display_df = results_df[display_metrics].copy()
    display_df.columns = [
        "# Ref Tok",
        "# Reas Tok",
        "# Answer Tokens",
        "ROUGE-1",
        "ROUGE-2",
        "ROUGE-L",
        "G-EVAL Coherence",
        "G-EVAL Fluency",
        "G-EVAL Relevance",
    ]

    # Display as formatted table
    styled_df = display_df.style.format("{:.0f}").background_gradient(cmap="Greens")

    return workflow_details, styled_df

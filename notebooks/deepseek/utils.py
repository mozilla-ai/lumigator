from time import sleep

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


def create_deepseek_config(
    model_name,
    ip_address,
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

    config["base_url"] = f"http://{ip_address}:8000/v1"

    return config

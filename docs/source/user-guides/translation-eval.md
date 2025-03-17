# Translation Use Case

This guide will walk you through the process of running a translation experiment using Lumigator with two models: a many-to-many sequence-to-sequence model from the Hugging Face Hub and `gpt-4o-mini` from  OpenAI.

## What You'll Need

1. A running instance of [Lumigator](../get-started/quickstart.md).
1. A dataset for translation use case. You can use the sample [English-Spanish dataset](../../../lumigator/sample_data/translation/sample_translation_en_es.csv) or prepare your own dataset. Refer to [this guide](./prepare-evaluation-dataset.md) for more details.
1. (Optional) An `OPENAI_API_KEY` if you would like to evaluate one of the OpenAI models. Please refer to the [UI instructions](../get-started/ui-guide.md#settings) for setting up the API keys.

## Procedure

To run a translation experiment, one can either use the UI or the API/SDK. If using the UI, we recommend following the steps in the [UI guide](../get-started/ui-guide.md) - from a high level, it will involve uploading the dataset and then creating an experiment (whereby you can select the use case as Translation, specify the source and targer language, and proceed with one or more of the available models). Once the experiment status is `SUCCEEDED`, you can view the experimental results in a tabular format.

Alternatively, you can also use the API/SDK to run the experiment. The following steps outline the process:

### Upload the Dataset
The dataset upload process is the same as outlined in the [quick start guide](../get-started/quickstart.md#upload-a-dataset). Simply update your `DATASET_PATH` to point to your translation dataset in csv format.

### Create an Experiment
Next, lets proceed to creating an experiment. The main point to note here is the `task_definition` field, which is a dictionary that specifies the task as `translation` and the `source_language` and the `target_language`.

::::{tab-set}

:::{tab-item} cURL
:sync: tab1

Set the following variables:
```console
user@host:~/lumigator$ export EXP_NAME="English to Spanish Translation" \
EXP_DESC="Evaluate which model best translates English to Spanish" \
EXP_DATASET="$(curl -s http://localhost:8000/api/v1/datasets/ | jq -r '.items | .[0].id')" \
TASK_DEFINITION='{"task": "translation", "source_language": "English", "target_language": "Spanish"}'
```

Define the JSON string:
```console
user@host:~/lumigator$ export JSON_STRING=$(jq -n \
--arg name "$EXP_NAME" \
--arg desc "$EXP_DESC" \
--arg dataset_id "$EXP_DATASET" \
--argjson task_definition "$TASK_DEFINITION" \
'{name: $name, description: $desc, dataset: $dataset_id, task_definition: $task_definition}')
```

Create the experiment:
```console
user@host:~/lumigator$ curl -s http://localhost:8000/api/v1/experiments/ \
-H 'Accept: application/json' \
-H 'Content-Type: application/json' \
-d "$JSON_STRING" | jq
{
  "id": "48",
  "name": "English to Spanish Translation",
  "description": "Evaluate which model best translates English to Spanish",
  "created_at": "2025-03-17T14:01:18.783000",
  "task_definition": {
    "task": "translation",
    "source_language": "English",
    "target_language": "Spanish"
  },
  "dataset": "4fbfc81d-938c-4703-beaf-af404fa5285f",
  "updated_at": null,
  "workflows": null
}
```

:::

:::{tab-item} Python SDK
:sync: tab2
```python
from lumigator_schemas.experiments import ExperimentCreate
dataset_id = datasets.items[-1].id
task_definition = {
    "task": "translation",
    "source_language": "English",
    "target_language": "Spanish"
}
request = ExperimentCreate(
    name = "English to Spanish Translation",
    description = "Evaluate which model best translates English to Spanish",
    dataset=dataset_id,
    task_definition=task_definition
)
experiment_response = client.experiments.create_experiment(request)
experiment_id = experiment_response.id
print(f"Experiment created and has ID: {experiment_id}")
```
:::

::::

## Trigger the Workflows
Next, lets trigger workflows to evaluate two models - `gpt-4o-mini` from OpenAI  and [`facebook/m2m100_418M`](https://huggingface.co/facebook/m2m100_418M) from Hugging Face Model Hub. This process can be repeated for as many models as you would like to evaluate in the experiment. In the workflow creation request, we also specify the following metrics to be computed: [BLEU](https://github.com/huggingface/evaluate/tree/main/metrics/bleu) and [METEOR](https://github.com/huggingface/evaluate/tree/main/metrics/meteor) which are word overlap metrics, and [COMET](https://unbabel.github.io/COMET/html/index.html) which is a neural translation metric.

::::{tab-set}

:::{tab-item} cURL
:sync: tab1

Set the following variables:
```console
user@host:~/lumigator$ export WORKFLOW_NAME="OpenAI Translation" \
WORKFLOW_DESC="Translate English to Spanish with OpenAI" \
WORKFLOW_DATASET="$(curl -s http://localhost:8000/api/v1/datasets/ | jq -r '.items | .[0].id')" \
EXPERIMENT_ID="$(curl -s http://localhost:8000/api/v1/experiments/ | jq -r '.items | .[0].id')" \
METRICS='["bleu", "meteor", "comet"]'
```

Define the JSON string:
```console
user@host:~/lumigator$ export JSON_STRING=$(jq -n \
--arg name "$WORKFLOW_NAME" \
--arg model "gpt-4o-mini" \
--arg provider "openai" \
--arg desc "$WORKFLOW_DESC" \
--arg dataset_id "$WORKFLOW_DATASET" \
--arg exp_id "$EXPERIMENT_ID" \
--argjson task_definition "$TASK_DEFINITION" \
--argjson metrics "$METRICS" \
'{name: $name, description: $desc, model: $model, provider: $provider, experiment_id: $exp_id, dataset: $dataset_id, task_definition: $task_definition, metrics: $metrics}')
```

Trigger the workflow:
```console
user@host:~/lumigator$ curl -s http://localhost:8000/api/v1/workflows/ \
-H 'Accept: application/json' \
-H 'Content-Type: application/json' \
-d "$JSON_STRING" | jq
{
  "id": "6e757bc0334645749d57023ed0a509df",
  "experiment_id": "48",
  "model": "gpt-4o-mini",
  "name": "OpenAI Translation",
  "description": "Translate English to Spanish with OpenAI",
  "system_prompt": "translate English to Spanish: ",
  "status": "created",
  "created_at": "2025-03-17T15:46:50.775000",
  "updated_at": null
}

:::

:::{tab-item} Python SDK
:sync: tab2
```python
from lumigator_schemas.workflows import WorkflowCreateRequest
metrics = [ "bleu", "meteor", "comet"]
request = WorkflowCreateRequest(
    name="OpenAI Translation",
    description="Translate English to Spanish with OpenAI",
    model="gpt-4o",
    provider="openai",
    dataset=dataset_id,
    experiment_id=experiment_id,
    task_definition=task_definition,
    metrics=metrics
)
client.workflows.create_workflow(request).model_dump()
```
:::

::::


##  Get the Results

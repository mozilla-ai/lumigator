# Translation Use Case

This guide will walk you through the process of running a translation experiment using Lumigator with two models: a many-to-many sequence-to-sequence model from the Hugging Face Hub and `gpt-4o-mini` from  OpenAI. Please refer to the list of [suggested models](../get-started/suggested-models.md#model-types-and-parameters) for translation use case for more details.

## What You'll Need

1. A running instance of [Lumigator](../get-started/quickstart.md).
1. A dataset for translation use case. You can use the [sample English-Spanish dataset](../../../lumigator/sample_data/translation/sample_translation_en_es.csv) or prepare your own dataset. Refer to [this guide](./prepare-evaluation-dataset.md) for more details.
1. (Optional) An `OPENAI_API_KEY` if you would like to evaluate one of the OpenAI models. Please refer to the [UI instructions](../get-started/ui-guide.md#settings) for setting up the API keys.

## Procedure

To run a translation experiment, one can either use the UI or the API/SDK. If using the UI, we recommend following the steps in the [UI guide](../get-started/ui-guide.md) - from a high level, it will involve uploading the dataset and then creating an experiment (whereby you can select the use case as Translation, specify the source and targer language, and proceed with one or more of the available models). Once the experiment status is `SUCCEEDED`, you can view the experimental results in a tabular format.

Alternatively, you can also use the API/SDK to run the experiment. The following steps outline the process:

### Upload the Dataset
The dataset upload process is the same as outlined in the [quick start guide](../get-started/quickstart.md#upload-a-dataset). Follow the upload dataset steps outlined there and then return to continue with the next steps below - don't forget to update your `DATASET_PATH` to point to your translation dataset in csv format.

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

### Trigger the Workflows
Next, lets trigger workflows to evaluate two models - `gpt-4o-mini` from OpenAI  and [`facebook/m2m100_418M`](https://huggingface.co/facebook/m2m100_418M) from Hugging Face Model Hub. This process can be repeated for as many models as you would like to evaluate in the experiment. In the workflow creation request, we also specify the following metrics to be computed: [BLEU](https://github.com/huggingface/evaluate/tree/main/metrics/bleu) and [METEOR](https://github.com/huggingface/evaluate/tree/main/metrics/meteor) which are word overlap metrics, and [COMET](https://unbabel.github.io/COMET/html/index.html) which is a neural translation metric.

Setup the following environment variables in a file called `common_variables.sh`:
```
#!/bin/bash
# Common API configuration for workflows
export WORKFLOW_DATASET="$(curl -s http://localhost:8000/api/v1/datasets/ | jq -r '.items | .[0].id')"
export EXPERIMENT_ID="$(curl -s http://localhost:8000/api/v1/experiments/ | jq -r '.items | .[0].id')"
export METRICS='["bleu", "meteor", "comet"]'
```

And then source the file:
```console
user@host:~/lumigator$ source common_variables.sh
```


::::{tab-set}

:::{tab-item} cURL (OpenAI)
:sync: openai-curl

Set the following variables:
```console
user@host:~/lumigator$ export WORKFLOW_NAME="OpenAI Translation" \
WORKFLOW_DESC="Translate English to Spanish with OpenAI"
```
Define the JSON string for OpenAI model:
```console
user@host:~/lumigator$ export JSON_STRING=$(jq -n \
--arg name "$WORKFLOW_NAME" \
--arg model "gpt-4o-mini" \
--arg provider "openai" \
--arg secret_key_name "openai_api_key" \
--arg desc "$WORKFLOW_DESC" \
--arg dataset_id "$WORKFLOW_DATASET" \
--arg exp_id "$EXPERIMENT_ID" \
--argjson batch_size 5 \
--argjson task_definition "$TASK_DEFINITION" \
--argjson metrics "$METRICS" \
'{name: $name, description: $desc, model: $model, provider: $provider, secret_key_name: $secret_key_name, batch_size: $batch_size, experiment_id: $exp_id, dataset: $dataset_id, task_definition: $task_definition, metrics: $metrics}')
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

:::{tab-item} SDK (OpenAI)
:sync: openai-python
```python
from lumigator_schemas.workflows import WorkflowCreateRequest

batch_size = 5
metrics = ["bleu", "meteor", "comet"]
request = WorkflowCreateRequest(
    name="OpenAI Translation",
    description="Translate English to Spanish with OpenAI",
    model="gpt-4o-mini",
    provider="openai",
    secret_key_name="openai_api_key",
    dataset=dataset_id,
    experiment_id=experiment_id,
    task_definition=task_definition,
    batch_size=batch_size,
    metrics=metrics
)
client.workflows.create_workflow(request).model_dump()
```
:::

:::{tab-item} cURL (Hugging Face)
:sync: hf-curl

Set the following variables:
```console
user@host:~/lumigator$ export WORKFLOW_NAME="Hugging Face Translation" \
WORKFLOW_DESC="Translate English to Spanish with M2M100"
```

Define the JSON string for HF model:
```console
user@host:~/lumigator$ export JSON_STRING=$(jq -n \
--arg name "$WORKFLOW_NAME" \
--arg model "facebook/m2m100_418M" \
--arg provider "hf" \
--arg desc "$WORKFLOW_DESC" \
--arg dataset_id "$WORKFLOW_DATASET" \
--arg exp_id "$EXPERIMENT_ID" \
--arg batch_size 5 \
--argjson task_definition "$TASK_DEFINITION" \
--argjson metrics "$METRICS" \
'{name: $name, description: $desc, model: $model, provider: $provider, experiment_id: $exp_id, batch_size: $batch_size, dataset: $dataset_id, task_definition: $task_definition, metrics: $metrics}')
```

Trigger the workflow:
```console
user@host:~/lumigator$ curl -s http://localhost:8000/api/v1/workflows/ \
-H 'Accept: application/json' \
-H 'Content-Type: application/json' \
-d "$JSON_STRING" | jq
{
  "id": "169c3169b7d549598b8b094c0dd9c806",
  "experiment_id": "48",
  "model": "facebook/m2m100_418M",
  "name": "Hugging Face Translation",
  "description": "Translate English to Spanish with M2M100",
  "system_prompt": "translate English to Spanish: ",
  "status": "created",
  "created_at": "2025-03-17T16:37:04.211000",
  "updated_at": null
}
```
:::

:::{tab-item} SDK (Hugging Face)
:sync: hf-python
```
from lumigator_schemas.workflows import WorkflowCreateRequest

batch_size = 5
metrics = ["bleu", "meteor", "comet"]
request = WorkflowCreateRequest(
    name="Hugging Face Translation",
    description="Translate English to Spanish with M2M100",
    model="facebook/m2m100_418M",
    provider="hf",
    dataset=dataset_id,
    experiment_id=experiment_id,
    task_definition=task_definition,
    batch_size=batch_size,
    metrics=metrics
)
client.workflows.create_workflow(request).model_dump()
```
:::

::::

## Verify
After the workflows has been triggered, you may need to wait a few minutes for the jobs to complete - you can check the status on the Experiments Page in the UI. Once completed, you can retrieve the experiment details with the following commands, allowing you to compare results and review performance. All the evaluation details can also be [viewed in the UI](../get-started/ui-guide.md#view-results).

::::{tab-set}

:::{tab-item} cURL
:sync: tab1

Set the following variables:
```console
user@host:~/lumigator$ export EXPERIMENT_ID="$(curl -s http://localhost:8000/api/v1/experiments/ | jq -r '.items | .[0].id')"
```

Get the experiment and check the `metrics` field for both the workflows:

```console
user@host:~/lumigator$ curl -s http://localhost:8000/api/v1/experiments/$EXPERIMENT_ID | jq
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
  "updated_at": "2025-03-17T14:01:18.783000",
  "workflows": [
    {
      "id": "169c3169b7d549598b8b094c0dd9c806",
      "experiment_id": "48",
      "model": "facebook/m2m100_418M",
      "name": "Hugging Face Translation",
      "description": "Translate English to Spanish with M2M100",
      "system_prompt": "translate English to Spanish: ",
      "status": "succeeded",
      "created_at": "2025-03-17T16:37:04.211000",
      "updated_at": null,
      "jobs": [
        {
          "id": "baa73e2a-3c81-4643-8797-513d31825922",
          "metrics": [
            {
              "name": "meteor_meteor_mean",
              "value": 0.811
            },
            {
              "name": "bleu_bleu_mean",
              "value": 0.472
            },
            {
              "name": "comet_mean_score",
              "value": 1.158
            }
          ],
          ...
```
:::

:::{tab-item} Python SDK
:sync: tab2
```python
experiment_details = lumi_client_int.experiments.get_experiment(experiment_id)
print(experiment_details.model_dump_json())
```
:::

::::


## Next Steps

You have successfully run an translation evaluation experiment using the Lumigator with a sample dataset. You can now test out other models on your own datasets or translation datasets from the [Hugging Face Hub](https://huggingface.co/datasets?task_categories=task_categories:translation&sort=downloads).

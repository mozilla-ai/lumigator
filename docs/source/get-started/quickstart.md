# Quickstart

You can deploy Lumigator either locally or into a distributed environment [using Kubernetes](../operations-guide/kubernetes-installation.md).
In this quickstart guide, we'll start Lumigator locally and evaluate a model on a dataset that we upload.
Looking to develop Lumigator? If so, you'll be interested in the [local development guide](../operations-guide/local-development.md) for details of running in development mode.

If you hit any issues running the quickstart, we want to hear about it! You can submit an issue [here](https://github.com/mozilla-ai/lumigator/issues).

## Prerequisites

Lumigator is currently supported on Linux and Mac. Windows is not yet tested, but we welcome contributions, see  {{ '[Contributing Guide](https://github.com/mozilla-ai/lumigator/blob/{}/CONTRIBUTING.md)'.format(commit_id) }}.

Before you start, make sure you have the following:

- A working installation of [Docker](https://docs.docker.com/engine/install/)
    - On Mac, Docker Desktop >= 4.37, and `docker-compose` >= 2.31.
    - On Linux, please also complete the [post-installation steps](https://docs.docker.com/engine/install/linux-postinstall/).
- The directory `$HOME/.cache/huggingface/` must exist and be readable and writeable. Lumigator uses this directory for accessing cached huggingface hub models.
- If you want to evaluate against hosted LLM APIs like the platforms provided by OpenAI, Mistral, or Deepseek, you need to set the appropriate environment variables before running Lumigator: `OPENAI_API_KEY` or `MISTRAL_API_KEY` or `DEEPSEEK_API_KEY`. They can either be set in the terminal you use to run the `start-lumigator` command, or they can be set in the .env file that lumigator automatically creates for you the first time you run it. Refer to the [troubleshooting section](../get-started/troubleshooting.md) for more details.
- If your system has an NVIDIA GPU, you need to have [installed the NVIDIA Container Toolkit following their instructions](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html). After that, open a terminal and run:
    ```bash
    export RAY_WORKER_GPUS=1
    export RAY_WORKER_GPUS_FRACTION=1.0
    export GPU_COUNT=1
    ```
    **Important: Run the next deployment steps in this same terminal, or thes env vars must be set in your shell configuration**

## Local Deployment

Lumigator is run locally using `docker-compose`. In order to deploy the latest release of Lumigator:

1. Clone the Lumigator repository:

    ```console
    user@host:~$ git clone git@github.com:mozilla-ai/lumigator.git
    ```

1. Change to the Lumigator directory:

    ```console
    user@host:~$ cd lumigator
    ```

1. Run the `start-lumigator` make target:

    ```console
    user@host:~/lumigator$ make start-lumigator
    ```

This will run all of the components needed for Lumigator.

This creates multiple container services networked together to make up all the components of the Lumigator application:

- `minio`: Local storage for datasets that mimics S3-API compatible functionality.
- `backend`: Lumigator’s FastAPI REST API. Access the Swagger HTTP Docs at http://localhost:8O00/docs
- `ray`: A Ray cluster for submitting several types of jobs. Access the Ray dashboard at http://localhost:8265
- `mlflow`: Used to track experiments and metrics, accessible at  http://localhost:8001
- `frontend`: Lumigator's Web UI, accessible at http://localhost:80

###  Verify

To verify that Lumigator is running, open a browser and navigate to `http://localhost:8000`. You
should receive the following JSON response:

```json
{"Hello": "Lumigator!🐊"}
```

## Using Lumigator

Now that Lumigator is deployed, we can use it to compare a few models. In this guide, we'll evaluate GPT-4o for a few samples of the [dialogsum](https://github.com/cylnlp/dialogsum) dataset that we store {{ '[here](https://github.com/mozilla-ai/lumigator/blob/{}/lumigator/sample_data/dialogsum_exc.csv)'.format(commit_id) }}.

We will show how to do this using either cURL or the Lumigator SDK. See [the UI guide](ui-guide.md) for information about how to use the UI.

The steps are as follows:

1. Upload the dialogsum dataset to Lumigator
1. Create an experiment, which is a container for running the workflow for each model
1. Run the summarization workflow for the model
1. Retrieve the results of the workflow

### Upload a Dataset

To upload a dataset, you need to send a POST request to the `/datasets` endpoint. The request should
include the dataset file.

To run this example, first `cd` to the `lumigator` directory. then run

::::{tab-set}

:::{tab-item} cURL
:sync: tab1
```console
user@host:~/lumigator$ export DATASET_PATH=lumigator/sample_data/dialogsum_exc.csv
user@host:~/lumigator$ curl -s http://localhost:8000/api/v1/datasets/ \
  -H 'Accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'dataset=@'$DATASET_PATH';type=text/csv' \
  -F 'format=job' | jq
{
  "id": "9ac42307-e0e5-4635-a9ce-48acdb451742",
  "filename": "dialogsum_exc.csv",
  "format": "job",
  "size": 3603,
  "ground_truth": true,
  "run_id": null,
  "generated": false,
  "generated_by": null,
  "created_at": "2025-02-19T20:00:01"
}
```
:::

:::{tab-item} Python SDK
:sync: tab2
```python
from lumigator_sdk.lumigator import LumigatorClient
from lumigator_schemas.datasets import DatasetFormat

dataset_path = 'lumigator/sample_data/dialogsum_exc.csv'
client = LumigatorClient('localhost:8000')

response = client.datasets.create_dataset(
    open(dataset_path, 'rb'),
    DatasetFormat.JOB
)
```
:::

::::

```{note}
The dataset file should be in CSV format and contain a header row with the following columns:
`examples`, `ground_truth`. The `ground_truth` column is optional since you can generate it using
Lumigator. See {{ '[here](https://github.com/mozilla-ai/lumigator/blob/{}/lumigator/sample_data/dialogsum_exc.csv#L4)'.format(commit_id) }}
for an example.
```

You can verify that the dataset was uploaded successfully by asking the API to list all datasets and
checking that the uploaded dataset is in the list:

::::{tab-set}

:::{tab-item} cURL
:sync: tab1
```console
user@host:~/lumigator$ curl -s http://localhost:8000/api/v1/datasets/ | jq -r '.items | .[] | .filename'
dialogsum_exc.csv
```
:::

:::{tab-item} Python SDK
:sync: tab2
```python
datasets = client.datasets.get_datasets()
print(datasets.items[-1].filename)
```
:::

::::

## Create an Experiment

Now that you have uploaded a dataset, you can create an experiment. An experiment is a container for running evaluations of models with the dataset. To this end, you need to
send a POST request to the `/experiments` endpoint. The request should include the following
required fields:

- A name for the experiment job.
- A short description.
- The ID of the dataset you want to use for evaluations.

Here is an example of how to create an experiment:

```{note}
the steps assume you only have uploaded a single dataset. If you have multiple datasets uploaded, replace the `"$(curl -s http://localhost:8000/api/v1/datasets/ | jq -r '.items | .[0].id')"` code with the ID of the dataset
```

::::{tab-set}

:::{tab-item} cURL
:sync: tab1

Set the following variables:
```console
user@host:~/lumigator$ export EXP_NAME="DialogSum Summarization" \
       EXP_DESC="See which model best summarizes Dialogues " \
       EXP_DATASET="$(curl -s http://localhost:8000/api/v1/datasets/ | jq -r '.items | .[0].id')"
```

Define the JSON string:
```console
user@host:~/lumigator$ export JSON_STRING=$(jq -n \
        --arg name "$EXP_NAME" \
        --arg desc "$EXP_DESC" \
        --arg dataset_id "$EXP_DATASET" \
        '{name: $name, description: $desc, dataset: $dataset_id}')
```

Create the experiment:
```console
user@host:~/lumigator$ curl -s http://localhost:8000/api/v1/experiments/ \
  -H 'Accept: application/json' \
  -H 'Content-Type: application/json' \
  -d "$JSON_STRING" | jq
{
  "id": "1",
  "name": "DialogSum Summarization",
  "description": "See which model best summarizes Dialogues ",
  "created_at": "2025-02-19T20:11:55.492000",
  "task": "summarization",
  "dataset": "9ac42307-e0e5-4635-a9ce-48acdb451742",
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
request = ExperimentCreate(
    name="DialogSum Summarization",
    description="See which model best summarizes Dialogues",
    dataset=dataset_id
)
experiment_response = client.experiments.create_experiment(request)
experiment_id = experiment_response.id
print(f"Experiment created and has ID: {experiment_id}")
```
:::

::::

## Trigger the workflows

Now it's time to evaluate a model! Let's trigger workflows to evaluate GPT-4o. This process can be repeated for as many models as you would like to evaluate in the experiment.


```{note}
the steps assume you only have created a single experiment. If you have multiple experiments, replace the `"$(curl -s http://localhost:8000/api/v1/experiments/ | jq -r '.items | .[0].id')"` code with the ID of the experiment you want
```

::::{tab-set}

:::{tab-item} cURL
:sync: tab1

Set the following variables:
```console
user@host:~/lumigator$ export WORKFLOW_NAME="OpenAI 4o" \
       WORKFLOW_DESC="Summarize with 4o" \
       WORKFLOW_DATASET="$(curl -s http://localhost:8000/api/v1/datasets/ | jq -r '.items | .[0].id')" \
       EXPERIMENT_ID="$(curl -s http://localhost:8000/api/v1/experiments/ | jq -r '.items | .[0].id')"
```

Define the JSON string:
```console
user@host:~/lumigator$ export JSON_STRING=$(jq -n \
        --arg name "$WORKFLOW_NAME" \
        --arg model "gpt-4o" \
        --arg provider "openai" \
        --arg desc "$WORKFLOW_DESC" \
        --arg dataset_id "$WORKFLOW_DATASET" \
        --arg exp_id "$EXPERIMENT_ID" \
        '{name: $name, description: $desc, model: $model, provider: $provider, experiment_id: $exp_id, dataset: $dataset_id}')
```

Trigger the workflow:
```console
user@host:~/lumigator$ curl -s http://localhost:8000/api/v1/workflows/ \
  -H 'Accept: application/json' \
  -H 'Content-Type: application/json' \
  -d "$JSON_STRING" | jq
{
  "id": "ffa38f72fe7e4b06a60de5bf797c31d6",
  "experiment_id": "1",
  "model": "gpt-4o",
  "name": "OpenAI 4o",
  "description": "Summarize with 4o",
  "status": "created",
  "created_at": "2025-02-19T20:30:33.713000",
  "updated_at": null
}

:::

:::{tab-item} Python SDK
:sync: tab2
```python
from lumigator_schemas.workflows import WorkflowCreateRequest
# Now let's run the same thing, but with o3-mini
request = WorkflowCreateRequest(
    name="OpenAI 4o",
    description="Summarize with 4o",
    model="gpt-4o",
    provider="openai",
    dataset=dataset_id,
    experiment_id=experiment_id
)
client.workflows.create_workflow(request).model_dump()
```
:::

::::

##  Get the results

Now that the workflow has been triggered we can get the experiment, which will give us all the details about the containing workflows. When the workflows are completed, this call will give you back all of the information about the evaluation, to let you compare results and review performance.

::::{tab-set}

:::{tab-item} cURL
:sync: tab1

Set the following variables:
```console
user@host:~/lumigator$ export EXPERIMENT_ID="$(curl -s http://localhost:8000/api/v1/experiments/ | jq -r '.items | .[0].id')"
```

Get the experiment!

```console
user@host:~/lumigator$ curl -s http://localhost:8000/api/v1/experiments/$EXPERIMENT_ID | jq
{
  "id": "1",
  "name": "DialogSum Summarization",
  "description": "See which model best summarizes Dialogues ",
  "created_at": "2025-02-19T20:11:55.492000",
  "task": "summarization",
  "dataset": "9ac42307-e0e5-4635-a9ce-48acdb451742",
  "updated_at": "2025-02-19T20:11:55.492000",
  "workflows": [
    {
      "id": "ffa38f72fe7e4b06a60de5bf797c31d6",
      "experiment_id": "1",
      "model": "gpt-4o",
      "name": "OpenAI 4o",
      "description": "Summarize with 4o",
      "status": "succeeded",
      "created_at": "2025-02-19T20:30:33.713000",
      "updated_at": null,
      "jobs": [...]
      "metrics": {
        "rouge1_mean": 0.224,
        "rouge2_mean": 0.106,
        "rougeL_mean": 0.195,
        "rougeLsum_mean": 0.195,
        "bertscore_f1_mean": 0.872,
        "bertscore_precision_mean": 0.866,
        "bertscore_recall_mean": 0.878,
        "meteor_mean": 0.276
      },
    }
  ]
}

:::

:::{tab-item} Python SDK
:sync: tab2
```python
experiment_details = lumi_client_int.experiments.get_experiment(experiment_id)
print(experiment_details.model_dump_json())
```
:::

::::

The metrics we use to evaluate are ROUGE, METEOR, and BERT score. They all measure similarity
between predicted summaries and those provided with the ground truth, but each of them focuses on
different aspects:

- [ROUGE](https://aclanthology.org/W04-1013.pdf) - (Recall-Oriented Understudy for Gisting
  Evaluation), which compares an automatically-generated summary to one generated by a machine
  learning model on a score of `0` to `1` in a range of metrics comparing statistical similarity of
  two texts.
- [METEOR](https://aclanthology.org/W05-0909.pdf) - Looks at the harmonic mean of precision and
  recall.
- [BERTScore](https://openreview.net/pdf?id=SkeHuCVFDr) - Generates embeddings of ground truth input
  and model output and compares their cosine similarity

## Terminate Session
In order to shut down Lumigator, you can stop the containers that were started using Docker Compose. This can be done by simply running the following command:
```console
user@host:~/lumigator$ make stop-lumigator
```

## Next Steps

Congratulations! You have successfully uploaded a dataset, created an experiment, run a model evaluation in the experiment, and retrieved
the results.

For info about developing lumigator, see the [local development guide](../operations-guide/local-development.md).

For information about deploying lumigator into a Kubernetes cluster, see [kubernetes installation](../operations-guide/kubernetes-installation.md).

# Quickstart

Now that you have a local deployment of Lumigator, you can start using it. In this quickstart guide,
we will show you how to upload a dataset and create a simple evaluation job. Finally, we'll show you
how to retrieve the results of the evaluation job.

## Upload a Dataset

The Lumigator backend provides an API endpoint for uploading datasets and running evaluation jobs.
To view the available endpoints, navigate to the API documentation page at
[`http://localhost:8000/docs`](http://localhost:8000/docs).

There are a few ways to interact with the API;

1. Test the endpoints via the OpenAPI documentation page at `http://localhost:8000/docs`
1. cURL commands.
1. The Lumigator Python SDK.

We'll focus on the last two.

To upload a dataset, you need to send a POST request to the `/datasets` endpoint. The request should
include the dataset file. Here is an example:

::::{tab-set}

:::{tab-item} cURL
:sync: tab1
```console
user@host:~/lumigator$ curl -s http://localhost:8000/api/v1/datasets/ \
  -H 'Accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'dataset=@'"path/to/dataset.csv"';type=text/csv' \
  -F 'format=experiment' | jq
{
  "id": "dd15bbaa-8d6f-44ae-a995-b3b78f4ea6fb",
  "filename": "dataset.csv",
  "format": "experiment",
  "size": 180528,
  "ground_truth": true,
  "created_at": "2024-10-30T12:10:18"
}
```
:::

:::{tab-item} Python SDK
:sync: tab2
```python
from lumigator_sdk.lumigator import LumigatorClient
from lumigator_schemas.datasets import DatasetFormat

dataset_path = 'path/to/dataset.csv'
lm_client = LumigatorClient('localhost:8000')

response = lm_client.datasets.create_dataset(
    open(dataset_path, 'rb'),
    DatasetFormat.JOB
)
```
:::

::::

```{note}
The dataset file should be in CSV format and contain a header row with the following columns:
`examples`, `ground_truth`. The `ground_truth` column is optional since you can generate it using
Lumigator. See [here](https://github.com/mozilla-ai/lumigator/blob/0bef1965c5180f39832e2932b59ef797b0853ff4/lumigator/python/mzai/sample_data/dialogsum_exc.csv#L4)
for an example.
```

You can verify that the dataset was uploaded successfully by asking the API to list all datasets and
checking that the uploaded dataset is in the list:

::::{tab-set}

:::{tab-item} cURL
:sync: tab1
```console
user@host:~/lumigator$ curl -s http://localhost:8000/api/v1/datasets/ | jq -r '.items | .[] | .filename'
dataset.csv
```
:::

:::{tab-item} Python SDK
:sync: tab2
```python
datasets = lm_client.datasets.get_datasets()
print(datasets.items[-1].filename)
```
:::

::::

## Create an Evaluation Job

Now that you have uploaded a dataset, you can create an evaluation job. To this end, you need to
send a POST request to the `/jobs/evaluate` endpoint. The request should include the following
required fields:

- A name for the evaluation job.
- A short description for tracking purposes.
- The name of the model you want to evaluate.
- The ID of the dataset you want to use for evaluation.
- The maximum number of examples to use for evaluation.

Here is an example of how to create an evaluation job:

::::{tab-set}

:::{tab-item} cURL
:sync: tab1

Set the following variables:
```console
user@host:~/lumigator$ export EVAL_NAME="test_run_hugging_face" \
       EVAL_DESC="Test run for Huggingface model" \
       EVAL_MODEL="hf://facebook/bart-large-cnn" \
       EVAL_DATASET="$(curl -s http://localhost:8000/api/v1/datasets/ | jq -r '.items | .[0].id')" \
       EVAL_MAX_SAMPLES="10"
```

Define the JSON string:
```console
user@host:~/lumigator$ export JSON_STRING=$(jq -n \
        --arg name "$EVAL_NAME" \
        --arg desc "$EVAL_DESC" \
        --arg model "$EVAL_MODEL" \
        --arg dataset_id "$EVAL_DATASET" \
        --arg max_samples "$EVAL_MAX_SAMPLES" \
        '{name: $name, description: $desc, model: $model, dataset: $dataset_id, max_samples: $max_samples}'
)
```

Create the evaluation job:
```console
user@host:~/lumigator$ curl -s http://localhost:8000/api/v1/jobs/evaluate/ \
  -H 'Accept: application/json' \
  -H 'Content-Type: application/json' \
  -d "$JSON_STRING" | jq
{
  "id": "3f15667d-d2e7-459b-9c22-3da2d236b406",
  "name": "test_run_hugging_face",
  "description": "Test run for Huggingface model",
  "status": "created",
  "created_at": "2024-10-31T09:07:43",
  "updated_at": null
}
```

:::

:::{tab-item} Python SDK
:sync: tab2
```python
from lumigator_schemas.jobs import JobType, JobEvalCreate

dataset_id = datasets.items[-1].id

models = ['hf://facebook/bart-large-cnn',]

# set this value to limit the evaluation to the first max_samples items (0=all)
max_samples = 10
# team_name is a way to group jobs together under the same namespace, feel free to customize it
team_name = "lumigator_enthusiasts"

responses = []
for model in models:
    job_args = JobEvalCreate(
        name=team_name,
        description="Test",
        model=model,
        dataset=str(dataset_id),
        max_samples=max_samples
    )
    # descr = f"Testing {model} summarization model on {dataset_name}"
    responses.append(lm_client.jobs.create_job(JobType.EVALUATION, job_args))
```
:::

::::

## Track the Evaluation Job

You can track the status of the evaluation job by sending a GET request to the `/jobs/{job_id}`
endpoint, or by using th Lumigator Python SDK. Here is an example of how to track the evaluation
job:

::::{tab-set}

:::{tab-item} cURL
:sync: tab1

Get the job's submission ID:

```console
user@host:~/lumigator$ export SUBMISSION_ID=$(curl -s http://localhost:8000/api/v1/health/jobs/ | jq -r 'sort_by(.start_time) | reverse | .[0] | .submission_id')
```

Track the job:

```console
user@host:~/lumigator$ curl -s "http://localhost:8000/api/v1/health/jobs/$SUBMISSION_ID" \
  -H 'Accept: application/json' | jq
{
  "type": "SUBMISSION",
  "job_id": null,
  "submission_id": "5195c9a5-938d-475e-b0fc-cf866492909d",
  "driver_info": null,
  "status": "SUCCEEDED",
  ...
}
```

:::

:::{tab-item} Python SDK
:sync: tab2
```python
job_id = responses[0].id

job = lm_client.jobs.wait_for_job(job_id)  # Create the coroutine object
result = await job  # Await the coroutine to get the result
```
:::

::::

## Retrieve the Results

Once the evaluation job is complete, you can retrieve the results by sending a GET request to the
`/jobs/{job_id}/result/download` endpoint, or by using the Lumigator Python SDK. This will return a
URI that you can use to download the results. Here is an example of how to retrieve the results:

::::{tab-set}

:::{tab-item} cURL
:sync: tab1

```console
user@host:~/lumigator$ curl -s http://localhost:8000/api/v1/jobs/$SUBMISSION_ID/result/download \
  -H 'accept: application/json' | jq
{
  "id": "5195c9a5-938d-475e-b0fc-cf866492909d",
  "download_url": "http://localhost:4566/lumigator-storage/jobs/results/lumigator_enthusiasts/5195c9a5-938d-475e-b0fc-cf866492909d/results.json?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=test%2F20241031%2Fus-east-2%2Fs3%2Faws4_request&X-Amz-Date=20241031T104126Z&X-Amz-Expires=3600&X-Amz-SignedHeaders=host&X-Amz-Signature=0309fe4825bc2358180c607a4a4ad4e8d36946133574d8b9416df228ce62944e"
}
```

:::

:::{tab-item} Python SDK
:sync: tab2
```python
import requests

eval_result = lm_client.jobs.get_job_download(job_id)
response = requests.request(url=eval_result.download_url, method="GET")
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
In order to shut down Lumigator, you can stop the containers that were [started](../get-started/installation.md) using Docker Compose. This can be done by simply running the following command:
```console
user@host:~/lumigator$ make stop-lumigator
```

## Next Steps

Congratulations! You have successfully uploaded a dataset, created an evaluation job, and retrieved
the results. In the next section, we will show you how to deploy Lumigator on a distributed
environment.

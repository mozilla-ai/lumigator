# Running an Inference Job

This guide will walk you through the process of running an inference job using the Lumigator SDK and
a model downloaded from the Hugging Face Hub. The model will generate summaries for a given set of
text data.

```{note}
You can also use the OpenAI GPT family of models or the Mistal API to run an inference job. To do
so, you need to set the appropriate environment variables: `OPENAI_API_KEY` or `MISTRAL_API_KEY`.
Refer to the `.env.example` file in the repository for more details.
```

## What You'll Need

- A running instance of [Lumigator](../get-started/installation.md).

## Procedure

1. Install the Lumigator SDK:

    ```console
    user@host:~/lumigator$ uv pip install -e lumigator/python/mzai/sdk
    ```

1. Create a new Python file:

    ```console
    user@host:~/lumigator$ touch inference.py
    ```

1. Add the following code to `inference.py`:

    ```python
    import json
    import requests

    from lumigator_sdk.lumigator import LumigatorClient
    from lumigator_schemas import jobs, datasets


    BUCKET = "lumigator-storage"
    HOST = "localhost"
    LUMIGATOR_PORT = 8000
    RAY_PORT = 4566


    # Instantiate the Lumigator client
    lm_client = LumigatorClient(f"{HOST}:{LUMIGATOR_PORT}")

    # Upload a dataset
    dataset_path = "lumigator/python/mzai/sample_data/dialogsum_exc.csv"
    dataset = lm_client.datasets.create_dataset(
        dataset=open(dataset_path, 'rb'),
        format=datasets.DatasetFormat.JOB
    )

    # Create and submit an inference job
    name = "bart-summarization-run"
    model = "hf://facebook/bart-large-cnn"
    task = "summarization"

    job_args = jobs.JobInferenceCreate(
        name=name,
        model=model,
        dataset=dataset.id,
        task=task,
    )

    job = lm_client.jobs.create_job(
        type=jobs.JobType.INFERENCE, request=job_args)

    # Wait for the job to complete
    lm_client.jobs.wait_for_job(job.id, poll_wait=10)

    # Retrieve the job results
    url = f"http://{HOST}:{RAY_PORT}/{BUCKET}/jobs/results/{name}/{job.id}/results.json"
    response = requests.get(url=url)

    if response.status_code != 200:
        raise Exception(f"Failed to retrieve job results: {response.text}")
    results = response.json()

    # Write the JSON results to a file
    with open("results.json", "w") as f:
        json.dump(results, f, indent=4)
    ```

1. Run the script:

    ```console
    user@host:~/lumigator$ uv run python inference.py
    ```

## Verify

Review the contents of the `results.json` file to ensure that the inference job ran
successfully:

```console
user@host:~/lumigator$ cat results.json | jq
{
"predictions": [
    "A man has trouble breathing. He is sent to see a pulmonary specialist. The doctor tests him for asthma. He does not have any allergies that he knows of. He also has a heavy feeling in his chest when he tries to breathe. This happens a lot when he works out, he says.",
...
```

## Next Steps

Congratulations! You have successfully run an inference job using the Lumigator SDK. You can now
use the results to evaluate your model's performance.

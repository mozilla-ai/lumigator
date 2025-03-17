# Running an Inference Job

This guide will walk you through the process of running an inference job using the Lumigator SDK and
a model downloaded from the Hugging Face Hub. The model will generate summaries for a given set of
text data.

This tutorial will show you how to perform inference as a single job. If you would like to do this as a part of an experiment and workflow (which includes evaluation of the results), see [the quickstart](../get-started/quickstart.md#using-lumigator).

```{note}
You can also use the OpenAI GPT family of models or the Mistral API to run an inference job. To do
so, you need to set the appropriate API key secrets beforehand.
Refer to [API settings configuration](../operations-guide/configuration#api-settings) for more details.
```

## What You'll Need

- A running instance of [Lumigator](../get-started/quickstart.md).

## Procedure

1. Install the Lumigator SDK:

    ```console
    user@host:~/lumigator$ uv pip install -e lumigator/sdk
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
    RAY_PORT = 8265


    # Instantiate the Lumigator client
    lm_client = LumigatorClient(f"{HOST}:{LUMIGATOR_PORT}")

   # Configure the client with the OpenAI API key as we plan to use OpenAI models.
   lm_client.settings.secrets.upload_api_key(APIKey.OPENAI, "YOUR_OPENAI_API_KEY") # pragma: allowlist secret

    # Upload a dataset
    dataset_path = "lumigator/sample_data/summarization/dialogsum_exc.csv"
    dataset = lm_client.datasets.create_dataset(
        dataset=open(dataset_path, 'rb'),
        format=datasets.DatasetFormat.JOB
    )

    # Create and submit an inference job
    name = "gpt-40-mini-summarization-run"
    model = "gpt-4o-mini"
    provider = "openai"

    job_create_request = jobs.JobCreate(
        name=name,
        dataset=dataset.id,
        job_config=jobs.JobInferenceConfig(
            model=model,
            provider=provider,
            secret_key_name=APIKey.OPENAI.name,
        ),
    )

    job = lm_client.jobs.create_job(job_create_request)

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

## Model Specification

Different models can be chosen for summarization.
The information about those models can be retrieved via the `http://<lumigator-host>:8000/api/v1/models/?tasks=summarization` endpoint.
It contains the following information for each model:

* `display_name`: an identification name for the model
* `model`: The model to use, e.g. `facebook/bart-large-cnn`
* `provider`: a URI specifying how and where to use the model. The following protocols are supported:
  * `hf`: direct model usage in an [HF pipeline](https://huggingface.co/docs/transformers/en/main_classes/pipelines)
  * Any protocol supported by [LiteLLM](https://docs.litellm.ai/docs/providers). For example, `openai/`, `mistral/`, `deepseek/`, etc.
* `base_url`: this field can be filled out if running a custom model that uses the openai protocol. For example, llamafile is generally hosted on your computer at `http://localhost:8080/v1`.
* `website_url`: a link to a web page with more information about the model
* `description`: a short description about the model
* `requirements`: additional requirements that need to be fulfilled before using the model
* `info`: a map containing information about the model like parameter count or model size
* `tasks`: a list of supported tasks, with parameters and capabilities appropriate to the task and their default or set values

Also, see: [Models API docs](https://mozilla-ai.github.io/lumigator/api/models.html) for more information.

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

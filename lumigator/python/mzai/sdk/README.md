# Lumigator SDK

The SDK provides the communication and validation primitives needed to contact the Lumigator itself,
either locally or remotely.

You can install the lumigator SDK  via `pip` directly or via `uv`:

```bash
pip install lumigator-sdk
```

or 

```bash
uv pip install lumigator-sdk
```


<<<<<<< HEAD
lumi_client = LumigatorClient("localhost:8000")
dialog_data = "dialogsum_exc.csv"

with Path.open(dialog_data) as file:
    datasets = lumi_client.datasets.get_datasets()
    if datasets.total > 0:
        for remove_ds in datasets.items:
            logger.info(f"Removing dataset {remove_ds.id}")
            lumi_client.datasets.delete_dataset(remove_ds.id)
    datasets = lumi_client.datasets.get_datasets()
    before = datasets.total
    dataset = lumi_client.datasets.create_dataset(dataset=file, format=DatasetFormat.JOB)
    datasets = lumi_client.datasets.get_datasets()
    assert datasets.total - before == 1
    jobs = lumi_client.jobs.get_jobs()
    assert jobs is not None
    print(lumi_client.datasets.get_dataset(dataset.id))
    job_create = JobEvalCreate(name="test-job-int-001", model="hf://distilgpt2", dataset=dataset.id)
    job_create.description = "This is a test job"
    job_create.max_samples = 0
    job_ret = lumi_client.jobs.create_job(JobType.EVALUATION, job_create)
    assert job_ret is not None
    jobs = lumi_client.jobs.get_jobs()
    assert jobs is not None
    assert len(jobs.items) == jobs.total

    job_status = asyncio.run(lumi_client.jobs.wait_for_job(job_ret.id))
    print(job_status)
```
=======
Now that you have the SDK installed, you can use it to communicate with Lumigator. You can run the
[example notebook](/notebooks/walkthrough.ipynb) for a platform API walkthrough, or follow the
[quickstart guide](https://mozilla-ai.github.io/lumigator/get-started/quickstart.html) in the
documentation.
>>>>>>> main

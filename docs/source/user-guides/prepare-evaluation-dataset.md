# Preparing Your Own Evaluation Dataset

If you need more information about what an evaluation dataset is and why it's important, check [this page](../conceptual-guides/datasets.md) first.

This guide will walk you through the process of preparing your own evaluation dataset
for Lumigator so you can compare the performance of multiple Language Models on your own use case, rather than on a generic benchmark.

This guide will cover the format Lumigator expects, what to focus on when collecting appropriate content and, lastly, how to upload and check that your resulting file is valid.

## Format

Lumigator expects a CSV file containing two columns, namely `examples` and `ground_truth`.

You can refer to the sample [dialogum dataset](../../../lumigator/sample_data/summarization/dialogsum_exc.csv ) for summarization use case and the sample [English-Spanish dataset](../../../lumigator/sample_data/translation/sample_translation_en_es.csv) for translation use case.


## Content

To prepare the samples that will actually be part of your dataset, you must collect, curate and annotate.

### 1. Collect

At worst, you will have to collect examples of input text manually.

At best, you already have a baseline system running; this could be first version of your application that may or may not be using a Language Model to do the task at hand (e.g. summarize), but it's already interfacing with users.

If it's already receiving input (i.e. examples) from users, you can automatically save them under the column `examples`.

```{note}
Ensure you are legally allowed and have collected consent from your users to collect this data.
```

At the end of this step, which may take anywhere between minutes and months (depending on your workflow), you should have a list of as many `examples` as possible of at least original texts from your domain.

For example, you can save them into a spreadsheet (if the process is manual) or a JSON file (if the process is automatic).

This will make exporting it to the CSV format that Lumigator currently supports less error-prone.


#### How many do you need?

Unfortunately, there is no clear-cut answer to this. Not as many as if you were training or fine-tuning a model, but remember: the more examples (and the higher quality they are), the more likely it is that a model score was not a fluke.

#### Example output

Feel free to collect your data into the format you are most comfortable with during your usual work. Bear in mind at the end you will have to export to CSV, but we do not encourage manually editing CSVs.

People manually collecting data may choose a spreadsheet, although if your workflow allows it, we encourage using JSON, JSONL, Pandas dataframes or HuggingFace datasets to automatically collect your data in.

Let's imagine you are building an app that summarizes patient history. After this collection step, your content may be dozens (or hundreds or thousands) of examples, such as:

```
    Patient A: 58-year-old male with persistent cough and chest pain for 3 months. CT scan revealed a lung mass. Biopsy and immunohistochemistry confirmed non-small cell lung cancer. Treatment: Surgical resection followed by chemotherapy.

    Patient J: 38-year-old female with thyroid nodule. Ultrasound-guided fine-needle aspiration and cytology were inconclusive. Surgical biopsy and frozen section analysis during surgery diagnosed papillary thyroid carcinoma. Treatment: Total thyroidectomy followed by radioactive iodine therapy.

    Patient K: 38-year-old woman presented with a thyroid mass. Initial diagnostic attempts using ultrasound-directed thin-needle sampling and cell examination yielded ambiguous results. Definitive diagnosis of papillary thyroid cancer was achieved through surgical tissue extraction and rapid intraoperative pathological assessment. The patient underwent complete removal of the thyroid gland, followed by treatment with radioiodine.

    Patient L: 38-year-old woman with thyroid mass. Ultrasound-directed thin-needle sampling and cell examination were inconclusive, later surgical tissue extraction and rapid intraoperative pathological assessment. Diagnosis: papillary thyroid cancer. Treatment was complete removal of the thyroid gland, followed by radioiodine therapy.

```

In this step, we are not adding ground truth, that is, we will not add what an ideal summary of each of those examples is.

### 2. Curate

This is the most time-intensive phase. Summon all your domain knowledge: which of those examples are basically the same as others? A few slightly paraphrased examples will help expose models that are too literal and have little robustness to synonyms, but if your whole dataset is built over 1000 ways of saying the same thing, the evaluation may not be the most meaningful.

For example, continuing with the example above, notice how similar the last 3 examples (Patients J, K and L) are. You might decide that only 1 is representative enough. Alternatively, you might want to leave Patients J and K, since it may be good to check that the model also understands longer form writing.

Your outcome, in that case, would be the list as above, minus Patient L.


### 3. Annotate (optional in Lumigator, but very strongly encouraged)

Regardless of the format you have been collecting your data in (spreadsheet, JSON, JSONL, HuggingFace datasets...), at the end of this final step, you will need to export to CSV.

Ground truth (i.e. the ideal output of the task for each example, as imagined by a human expert) is crucial to evaluate a Language Model. Lumigator allows you to upload a dataset with only the `examples` column and later annotate the dataset with a high-quality Language Model, but nobody has vetted that Language Model for your use case: we cannot guarantee it knows as much about your business as you do.

If you do have human experts who were able to go through the input data from step #2 and add their annotations, you should end up with a file with the same list of examples, plus the annotation after a comma.


#### Example output

After exporting to CSV, this is what the end file should look like.

```
examples,ground_truth
"Patient A: 58-year-old male with persistent cough and chest pain for 3 months. CT scan revealed a lung mass. Biopsy and immunohistochemistry confirmed non-small cell lung cancer. Treatment: Surgical resection followed by chemotherapy.","58M, lung cancer diagnosed via CT and biopsy, treated with surgery and chemo."
"Patient J: 38-year-old female with thyroid nodule. Ultrasound-guided fine-needle aspiration and cytology were inconclusive. Surgical biopsy and frozen section analysis during surgery diagnosed papillary thyroid carcinoma. Treatment: Total thyroidectomy followed by radioactive iodine therapy.","38F, thyroid cancer confirmed through surgical biopsy, treated with thyroidectomy and radioiodine."
"Patient K: 38-year-old woman presented with a thyroid mass. Initial diagnostic attempts using ultrasound-directed thin-needle sampling and cell examination yielded ambiguous results. Definitive diagnosis of papillary thyroid cancer was achieved through surgical tissue extraction and rapid intraoperative pathological assessment. The patient underwent complete removal of the thyroid gland, followed by treatment with radioiodine.","38F, thyroid cancer confirmed through surgical biopsy, treated with thyroidectomy and radioiodine."
```


## Validate your dataset file

Now that you have a dataset (let's assume it's `my_dataset.csv`), let's upload it to Lumigator and check everything is fine.

You can do this via the [UI](../get-started/ui-guide.md) or, as below, via the SDK.


### What You'll Need

- A running instance of [Lumigator](../get-started/quickstart.md).

#### Procedure

1. Install the Lumigator SDK:

    ```console
    user@host:~/lumigator$ uv pip install -e lumigator/sdk
    ```

1. Add the following code to a new Python file, `upload_dataset.py`:

    ```python
    import json
    import requests
    from lumigator_schemas import datasets
    from lumigator_sdk.lumigator import LumigatorClient

    # Instantiate the Lumigator client
    lm_client = LumigatorClient("localhost:8000")

    # Upload the dataset
    dataset_path = "my_dataset.csv"
    dataset = lm_client.datasets.create_dataset(dataset=open(dataset_path, "rb"), format=datasets.DatasetFormat.JOB)

    # Check the dataset was correctly added
    print(lm_client.datasets.get_dataset(dataset.id))

    ```

1. Run the script:

    ```console
    user@host:~/lumigator$ uv run python upload_dataset.py
    ```


#### But I was already using HuggingFace Datasets...

Excellent. Below is an example of how to turn a huggingface dataset into one that is compatible with Lumigator.

```python

  from datasets import load_dataset
  from lumigator_schemas.datasets import DatasetFormat
  from lumigator_sdk.lumigator import LumigatorClient

  # First, grab the dataset off huggingface: https://huggingface.co/datasets/YuanPJ/summ_screen
  ds = load_dataset("YuanPJ/summ_screen", "fd")["test"]

  # Now let's prepare it for Lumigator upload. We need to rename some columns and delete the rest
  # rename the column "input" to "text" and "output" to "ground_truth". This is what Lumigator expects
  ds = ds.rename_column("Transcript", "examples")
  ds = ds.rename_column("Recap", "ground_truth")

  # remove all columns except "text" and "ground_truth"
  columns_list = ds.column_names
  columns_list.remove("examples")
  columns_list.remove("ground_truth")
  ds = ds.remove_columns(columns_list)

  # convert ds to a csv and make it a string so we can upload it with the Lumigator API
  DS_OUTPUT = "summ_screen.csv"
  ds.to_csv(DS_OUTPUT)

  # Time to connect up to the Lumigator client!
  HOST = "localhost:8000"
  client = LumigatorClient(api_host=HOST)

  # Upload that file that we created earlier
  with Path.open(DS_OUTPUT) as file:
      data = file.read()
  dataset_response = client.datasets.create_dataset(dataset=data, format=DatasetFormat.JOB)

  # Check the dataset was correctly added
  print(lm_client.datasets.get_dataset(dataset.id))

```

#### Verify

Regardless of the method, you should see a confirmation that looks like:

```console
id=UUID('421f6d8a-0e9c-45c9-bb3b-8a3badf01235') filename='my_dataset.csv' format=<DatasetFormat.JOB: 'job'> size=3992 ground_truth=True run_id=None generated=False generated_by=None created_at=datetime.datetime(2025, 2, 25, 17, 57, 55)
```


## Next Steps

Congratulations! You have successfully created an evaluation dataset and uploaded it using the Lumigator SDK. You can now start comparing models with each other for your use case!

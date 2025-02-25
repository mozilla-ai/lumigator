Datasets API
============
The Datasets API allows users to manage datasets within Lumigator. Users can upload datasets,
which are then parsed into HuggingFace format files and stored alongside a recreated version of the input dataset.

The file you upload must be a CSV file with a header row. There must be a column called 'examples' which is the input data.
There may also be a column called 'ground_truth' which is the target data. If you don't have a 'ground_truth' column,
Lumigator will use an LLM to generate the target data for you.


Example
-------

Below is an example of how to turn a huggingface dataset into one that is compatible with Lumigator.

.. code-block:: python

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
  LUMI_HOST = "localhost:8000"
  client = LumigatorClient(api_host=LUMI_HOST)

  # Upload that file that we created earlier
  with Path.open(DS_OUTPUT) as file:
      data = file.read()
  dataset_response = client.datasets.create_dataset(dataset=data, format=DatasetFormat.JOB)


The API provides endpoints to list all datasets, retrieve details of a specific dataset,
delete a dataset, and download datasets.
The upload process ensures that the dataset is compatible with HuggingFace standards,
although the recreated CSV file may have different delimiters.
The API supports various operations with appropriate status codes to indicate the success or failure of each request.

Endpoints
---------

.. openapi:: ../specs/openapi.json
   :include:
     /api/v1/datasets/*

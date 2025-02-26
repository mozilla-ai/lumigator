Datasets API
============

A dataset is a collection of data points (or samples) used for training, testing, or evaluating machine learning models.

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

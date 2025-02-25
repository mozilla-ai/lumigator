Jobs API
============

A job is designed to execute a specific task on the Ray cluster.
Jobs are created by the backend and are executed on the Ray cluster.

For example, a job may run inference with a model to generate ground truth for a dataset.
Or, a job may evaluate the outputs of an inference job against the ground truth stored in the dataset.

Endpoints
---------

.. openapi:: ../specs/openapi.json
   :include:
     /api/v1/jobs/*

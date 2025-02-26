Workflows API
=============

Workflows are designed to manage and run multiple atomic jobs. Jobs are designed to execute specific tasks on the Ray cluster,
for example performing inference of a model using a dataset that was uploaded. Workflows are designed to be a way to link
these jobs together.

For example, in order to evaluate how a model performs on a summarization task, there are two jobs that must be executed.
First, an inference job runs in order to run inference with a model and collect the outputs. Next, an evaluation job
runs in order to evaluate the outputs of the inference job against the ground truth stored in the dataset.

Endpoints
---------

.. openapi:: ../specs/openapi.json
   :include:
     /api/v1/workflows/*

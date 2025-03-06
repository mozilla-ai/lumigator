Experiments API
===============

The Experiments API allows you to manage experiments within the system.
This API provides endpoints to create, list, retrieve, and delete experiments.

An experiment, in this context, is defined as the execution of different models—each running as an individual job—using the same dataset prepared for a specific use case.

This approach helps group related evaluations together, enabling consistent and reproducible testing. Additionally, experiments may include any extra information or links to internal structures that further detail the experiment setup, without overcomplicating the documentation.
Endpoints
---------

.. openapi:: ../specs/openapi.json
   :include:
     /api/v1/experiments/*

Experiments API
===============

The Experiments API allows you to manage experiments within the system.
This API provides endpoints to create, list, retrieve, and delete experiments.

An experiment is meant to be a container for the evaluations you run with different models:
this allows for a method to conveniently group evaluations together and retrieve their results.

Endpoints
---------

.. openapi:: ../specs/openapi.json
   :include:
     /api/v1/experiments/*

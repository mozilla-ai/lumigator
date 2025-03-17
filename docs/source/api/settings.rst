Settings API
============

Many APIs require some sort of secret or token to be able to work on them. They are usually stored in
environment variables in personal use, like `OPENAI_API_KEY` or `MISTRAL_API_KEY`.

For added security, the Lumigator API allows the user to store secrets as encoded values in its database,
which will be used in requests but will not be returned in the API.

Endpoints
---------

.. openapi:: ../specs/openapi.json
   :include:
     /api/v1/settings/*

.. You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Mozilla.ai Lumigator
====================

Lumigator is an open-source platform built by Mozilla.ai for guiding users through the process of
selecting the right language model for their needs.

Currently, we support evaluating summarization
tasks using sequence-to-sequence models, like BART, and causal architectures, like
Mistral.

These models can either be loaded and run by Lumigator
(if they are models stored in `Huggingface Hub <https://huggingface.co/models>`_), or the models can be reached through any OpenAI
compatible interface (for example, llamafile or OpenAI GPT models). Lumigator will soon
support additional tasks such as translation  (See `#628 <https://github.com/mozilla-ai/lumigator/issues/628>`_).

.. note::

   Lumigator is in the early stages of development. It is missing important features and
   documentation. You should expect breaking changes in the core interfaces and configuration
   structures as development continues.

Overview
--------

Lumigator contains several different components and can be used in a few different ways.

The core functionality is the backend, which is a Python-based FastAPI server that features REST API endpoints.

These REST API endpoints can be accessed by a variety of clients, including:

   - A Web UI (See :doc:`get-started/ui-guide`)
   - A Python SDK (See :doc:`reference/sdk`)
   - Any http client, like cURL (See :doc:`reference/schemas`)

The backend is responsible for receiving requests from clients and managine the lifecycle of
datasets, experiments, workflows, and jobs.
The backend also coordinates interaction with a Ray cluster and a database. The Ray cluster is used to run jobs, and
the database is used to store metadata about the platform, jobs, and datasets.

For more information about datasets, see :doc:`api/datasets`.

For more information about experiments, see :doc:`api/experiments`.

For more information about workflows, see :doc:`api/workflows`.

For more information about jobs, see :doc:`api/jobs`.

For more information about the backend routes, see the rendered API specs in the :doc:`API Specs <api/index>`.

.. toctree::
   :maxdepth: 1
   :caption: Get Started

   get-started/quickstart
   get-started/development-guide
   get-started/ui-guide
   get-started/suggested-models
   get-started/troubleshooting

.. toctree::
   :maxdepth: 2
   :caption: Operations Guide

   operations-guide/configuration
   operations-guide/kubernetes-installation
   operations-guide/alembic
   operations-guide/dev
   operations-guide/configure-S3

.. toctree::
   :maxdepth: 2
   :caption: User Guides

   user-guides/inference
   user-guides/local-models

.. toctree::
   :maxdepth: 2
   :caption: Conceptual Guides

   conceptual-guides/architecture

.. toctree::
   :maxdepth: 1
   :caption: Reference

   reference/sdk
   reference/schemas

.. toctree::
   :caption: API Specifications

   api/index

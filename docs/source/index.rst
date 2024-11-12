.. Lumigator documentation master file, created by
   sphinx-quickstart on Tue Oct 29 13:57:02 2024.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Mozilla.ai Lumigator
====================

Lumigator is an open-source platform built by Mozilla.ai for guiding users through the process of
selecting the right language model for their needs. Currently, we support evaluating summarization
tasks using sequence-to-sequence models, like BART and BERT, and causal architectures, like GPT and
Mistral. However, we will be expanding to other machine learning tasks and use-cases.

.. note::

   Lumigator is in the early stages of development. It is missing important features and
   documentation. You should expect breaking changes in the core interfaces and configuration
   structures as development continues.

Overview
--------

Lumigator is a Python-based FastAPI web app that features REST API endpoints, providing access to
services for serving and evaluating large language models. These models can be hosted on both
Hugging Face and local stores or accessed through APIs. It consists of:

   - A FastAPI-based web app that provides various endpoints for serving and evaluating language
     models.
   - A Ray cluster to run offline inference or evaluation jobs.
   - Artifact management (S3 in the cloud, localstack locally).
   - A database to track platform-level lifecycle, job, and dataset metadata.

.. toctree::
   :maxdepth: 2
   :caption: Get Started

   get-started/installation
   get-started/quickstart

.. toctree::
   :maxdepth: 2
   :caption: Operation Guides

   operation-guides/kubernetes
   operation-guides/alembic

.. TODO: Add user-guides and examples here.
.. .. toctree::
..    :maxdepth: 2
..    :caption: User Guides

..    user-guides/evaluation

.. toctree::
   :maxdepth: 2
   :caption: Conceptual Guides

   conceptual-guides/endpoints
   conceptual-guides/new-endpoint

.. toctree::
   :maxdepth: 1
   :caption: Reference

   reference/sdk
   reference/schemas

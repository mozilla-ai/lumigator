# Lumigator

Lumigator is an open-source platform developed by [Mozilla.ai](https://www.mozilla.ai/) designed to
help users select the most appropriate language model for their needs. It supports tasks such as
evaluating summarization using sequence-to-sequence models (like BART and BERT) and causal models
(like GPT and Mistral), with plans to expand to other machine learning tasks and use cases in the
future.

## `infra` Directory

The `infra` directory contains all necessary infrastructure files for deploying Lumigator,
including:

- **HELM charts**: For deploying Lumigator on Kubernetes.
- **YAML configuration files**: For deploying Ray clusters.

## `python` Directory

The `python` directory contains the source code for the core functionality of Lumigator,
including:

- **SDK**: A Python SDK for interacting with Lumigator services.
- **Backend API**: The backend API that makes the platform's features available.

## `frontend` Directory

The `frontend` directory contains the source code for Lumigator frontend.

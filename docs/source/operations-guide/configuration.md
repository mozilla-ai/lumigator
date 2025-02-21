# Configuring Lumigator

```{note}
This guide only covers configuring Lumigator when deployed using Docker.
```

Lumigator comes with sensible defaults that allow you to [start using it](../get-started/quickstart.md) without modification using [`Docker Compose`](https://docs.docker.com/compose/).

This guide explains how configuration works in Lumigator and how you can make changes to settings if required.

## Where are the config files?

The default Lumigator settings are found in the repository root under {{ '[`.default.conf`](https://github.com/mozilla-ai/lumigator/blob/{}/.default.conf)'.format(commit_id) }}.

They are specified in key=value format within the config file.

## How are these settings used?

When you start Lumigator using commands like `make local-up` or `make start-lumigator`, configuration steps are automatically run which do the following:

1. Any temporary config files used for deployment are removed
1. Default and user settings (if present) are combined (with user settings preferred - see below for information on using your own settings)
1. These settings are also combined with the user stored `LUMIGATOR_SECRET_KEY` - see below for more information on the secret key
1. The generated config file (`.env`) is placed under the `build` directory in the repository root
1. Docker Compose is supplied with the environment file path to the generated `.env` file

From there the `.env` file variables are used in Lumigator's application or supplied to components (such as Ray, MinIO, MLFlow).

When you stop Lumigator using commands like `make local-down` or `make stop-lumigator`, the temporary files stored under `build` are removed. While Lumigator is running they are present if you wish to examine their contents.

```{note}
The `build` directory and the user defined config file are both marked in `.gitignore`
```

## How should I set my own settings?

User specific configuration can be stored in a file named `user.conf` in under `${HOME}/.lumigator`, this file is configured in `.gitignore` for safety, but should never appear in your repo directory.

`user.conf` must be created manually when required, **only** add key/values for the settings you explicitly wish to change from the defaults.

Any settings not included in `user.conf` will automatically fall back to the default settings when running Lumigator.

Please review `.default.conf` for the format, setting names and default values (also see below for a quick reference).

## Can I configure everything?

Not currently, there are a lot of settings available in `.default.conf` but for example you cannot yet change the URL that is exposed via FastAPI on our Backend component from http://localhost:8000.

You cannot configure the user secret key under `LUMIGATOR_SECRET_KEY` as the value for this key **must** be read from the Lumigator dot fodler in the user's home directory.

## What is the secret key?

Lumigator requires a (symmetric) secret key which is used for encrypting and decrypting specific settings (secrets) stored via the API.

The key will be created and stored automatically (if it is not present) on startup. The path Lumigator expects to find the key is:

```bash
${HOME}/.lumigator/lumigator.key`
```

During deployment, when the `build/.env` file is generated, this key will be merged into the `.env` with the key name `LUMIGATOR_SECRET_KEY`.

Due to the sensitive nature of the key, you cannot override the value for LUMIGATOR_SECRET_KEY that appears
in the .env using user.conf.

It will be read from ${HOME}/.lumigator/lumigator.key, and must be present.

```{note}
Please ensure you have not exported LUMIGATOR_SECRET_KEY as this will conflict with the accurate value in the generated .env file.
```

Once the key is generated, it should not be changed otherwise any data stored in Lumigator's databse will become unreadable.

Additionally it is the user's responsibility to ensure this key is kept safe. The only place it can exist
within the Lumigator repo is in the `buid/.env` file that is automatically removed when you call `make local-down` or `make stop-lumigator`.

## Settings

The following section documents the available settings:

> [!Note]
> To use an external Ray cluster, you **must** use external S3-compatible storage and ensure the Ray workers can access data from your Lumigator server.

| Name                               | Type    | Description                                                                                                                |
|------------------------------------|---------|----------------------------------------------------------------------------------------------------------------------------|
| AWS_ACCESS_KEY_ID                  | string  | AWS credential, used for auth with S3 services (e.g. MinIO)                                                                |
| AWS_SECRET_ACCESS_KEY              | string  | Sensitive AWS secret, used for auth with S3 services (e.g. MinIO)                                                          |
| AWS_DEFAULT_REGION                 | string  | AWS default region name                                                                                                    |
| AWS_ENDPOINT_URL                   | string  | URL used to contact S3 services (e.g. MinIO)                                                                               |
| S3_BUCKET                          | string  | The S3 bucket name to store Lumigator data under                                                                           |
| RAY_HEAD_NODE_HOST                 | string  | The hostname of the head Ray node that Lumigator should contact                                                            |
| RAY_DASHBOARD_PORT                 | integer | The dashboard port for the Ray cluster that Lumigator is interacting with                                                  |
| RAY_WORKER_GPUS                    | integer | The number of worker GPUs available to Ray that should be used for jobs                                                    |
| RAY_WORKER_GPUS_FRACTION           | float   | If not `0`, the fraction of the worker GPUs that should be used by a Ray job                                               |
| NVIDIA_VISIBLE_DEVICES             | string  | Defaults to 'all', specifies which NVIDIA devices should be visible to Ray                                                 |
| GPU_COUNT                          | int     | The number of GPUs                                                                                                         |
| HF_HOME                            | string  | The home directory for HuggingFace (used for caching)                                                                      |
| HF_TOKEN                           | string  | Sensitive API token used to access gated models in HuggingFace                                                             |
| MISTRAL_API_KEY                    | string  | Sensitive API key used to access Mistral                                                                                   |
| OPENAI_API_KEY                     | string  | Sensitive API key used to access OpenAI                                                                                    |
| MLFLOW_TRACKING_URI                | string  | The URL used to access MLFlow                                                                                              |
| MLFLOW_DATABASE_URL                | string  | DB connection string/URL used for MLFlow                                                                                   |
| MLFLOW_S3_ROOT_PATH                | string  | S3 URL styl path to the root where MFLow should store artefacts  e.g. S3://mflow                                           |
| MINIO_ROOT_USER                    | string  | The root user name for accessing MinIO                                                                                     |
| MINIO_ROOT_PASSWORD                | string  | Sensitive secret for accessing MinIO as root                                                                               |
| MINIO_API_CORS_ALLOW_ORIGIN        | string  | Allowed origins for CORS requests to MinIO (defaults to "*")                                                               |
| DEPLOYMENT_TYPE                    | string  | Allows the user to define which environment Lumigator is deployed in, local', 'development', 'staging' or 'production'     |
| DATABASE_URL                       | string  | DB connection string/URL used for Lumigator's local DB storage                                                             |
| LUMIGATOR_API_CORS_ALLOWED_ORIGINS | string  | A comma separated string array of URLs which should be allowed origins for CORS requests, "*" can be supplied to allow all |
| INFERENCE_PIP_REQS                 | string  | Path within the container to the requirements.txt file for inference jobs                                                  |
| INFERENCE_WORK_DIR                 | string  | Path within the container to the working directory that is zipped and sent to Ray as an inference job                      |
| EVALUATOR_PIP_REQS            | string  | Path within the container to the requirements.txt file for evaluation jobs                                          |
| EVALUATOR_WORK_DIR            | string  | Path within the container to the working directory that is zipped and sent to Ray as an evaluation job              |

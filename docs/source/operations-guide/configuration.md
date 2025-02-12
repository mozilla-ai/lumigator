# Configuring Lumigator

> [!NOTE]
> This guide only covers configuring Lumigator when deployed using Docker.

Lumigator comes with sensible defaults that allow you to [start using it](../get-started/installation.md) without modification using [`Docker Compose`](https://docs.docker.com/compose/).

This guide explains how configuration works in Lumigator and how you can make changes to settings if required.

## Where are the config files?

The default Lumigator settings are found in the repository root under {{ '[`config.default.yaml`](https://github.com/mozilla-ai/lumigator/blob/{}/config.default.yaml)'.format(commit_id) }}.

They are specified in `YAML` and at present all settings are under `app` section within the config file.

## How are these settings used?

When you start Lumigator using commands like `make local-up` or `make start-lumigator`, configuration steps are automatically run which do the following:

1. Any temporary config files used for deployment are removed
1. Default and user settings are combined (with user settings prefered - see below for information on using your own settings)
1. The generated config file (`config.deploy.yaml`) is placed under the `build` directory in the repository root
1. `config.deploy.yaml` is used to generate a `.env` file (also stored under the `build` directory)
1. Docker Compose is supplied with the environment file path to the generated `.env` file

From there the `.env` file variables are used in Lumigator's application or supplied to components (such as Ray, MinIO, MLFlow).

When you stop Lumigator using commands like `make local-down` or `make stop-lumigator`, or detach from `make local-up`, the temporary files stored under `build` are removed. While Lumigator is running they are present if you wish to examine their contents.

> [!NOTE]
> The `build` directory is marked in `.gitignore`

## How should I set my own settings?

User specific configuration is stored in a file named `config.user.yaml`, this file is configured in `.gitignore` and will never be commited to version control.

It is possible to manually create the `config.user.yaml` file and only add key/values for the settings you wish to change from the defaults. Please review `config.default.yaml` for the format.

Alternatively, you can generate the user config file using the `config-generate` `Makefile` target:

```console
user@host:~/lumigator$ make config-generate
```

You can edit this file to update your settings, remove any settings you don't want to explicitly set, and the defaults for those settings will always be used when running Lumigator.

## Can I configure everything?

Not currently, there are a lot of settings available in `config.default.yaml` but for example you cannot yet change the URL that is exposed via FastAPI on our Backend component from http://localhost:8000.

## Settings

The following section documents the available settings for `app`.

> [!Note]
> To use an external Ray cluster, you **must** use external S3-compatible storage and ensure the Ray workers can access data from your Lumigator server.

| Name                               | Type    | Description                                                                                                            |
|------------------------------------|---------|------------------------------------------------------------------------------------------------------------------------|
| aws_access_key_id                  | string  | AWS credential, used for auth with S3 services (e.g. MinIO)                                                            |
| aws_secret_access_key              | string  | Sensitive AWS secret, used for auth with S3 services (e.g. MinIO)                                                      |
| aws_default_region                 | string  | AWS default region name                                                                                                |
| aws_endpoint_url                   | string  | URL used to contact S3 services (e.g. MinIO)                                                                           |
| s3_bucket                          | string  | The S3 bucket name to store Lumigator data under                                                                       |
| ray_head_node_host                 | string  | The hostname of the head Ray node that Lumigator should contact                                                        |
| ray_dashboard_port                 | integer | The dashboard port for the Ray cluster that Lumigator is interacting with                                              |
| ray_worker_gpus                    | integer | The number of worker GPUs available to Ray that should be used for jobs                                                |
| ray_worker_gpus_fraction           | float   | If not `0`, the fraction of the worker GPUs that should be used by a Ray job                                           |
| nvidia_visible_devices             | string  | Defaults to 'all', specifies which NVIDIA devices should be visible to Ray                                             |
| gpu_count                          | int     | The number of GPUs                                                                                                     |
| hf_home                            | string  | The home directory for HuggingFace (used for caching)                                                                  |
| hf_token                           | string  | Sensitive API token used to access gated models in HuggingFace                                                         |
| mistral_api_key                    | string  | Sensitive API key used to access Mistral                                                                               |
| openai_api_key                     | string  | Sensitive API key used to access OpenAI                                                                                |
| mlflow_tracking_uri                | string  | The URL used to access MLFlow                                                                                          |
| mlflow_database_url                | string  | DB connection string/URL usef for MLFlow                                                                               |
| mlflow_s3_root_path                | string  | S3 URL styl path to the root where MFLow should store artefacts  e.g. S3://mflow                                       |
| minio_root_user                    | string  | The root user name for accessing MinIO                                                                                 |
| minio_root_password                | string  | Sensitive secret for accessing MinIO as root                                                                           |
| minio_api_cors_allow_origin        | string  | Allowed origins for CORS requests to MinIO (defaults to "*")                                                           |
| deployment_type                    | string  | Allows the user to define which environment Lumigator is deployed in, local', 'development', 'staging' or 'production' |
| database_url                       | string  | DB connection string/URL used for Lumigator's local DB storage                                                         |
| lumigator_api_cors_allowed_origins | array   | A string array of URLs which should be allowed origins for CORS requests, "*" can be supplied to allow all             |
| inference_pip_reqs                 | string  | Path within the container to the requirements.txt file for inference jobs                                              |
| inference_work_dir                 | string  | Path within the container to the working directory that is zipped and sent to Ray as an inference job                  |
| evaluator_pip_reqs                 | string  | Path within the container to the requirements.txt file for evaluation jobs                                             |
| evaluator_work_dir                 | string  | Path within the container to the working directory that is zipped and sent to Ray as an evaluation job                 |
| evaluator_lite_pip_reqs            | string  | Path within the container to the requirements.txt file for evaluation (lite) jobs                                      |
| evaluator_lite_work_dir            | string  | Path within the container to the working directory that is zipped and sent to Ray as an evaluation (lite) job          |

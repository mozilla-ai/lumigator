# Local Development

This guide will walk you through setting up a local development environment for Lumigator backend.
This is useful for testing changes to the backend codebase during development or for debugging
issues. Reading this guide is a must if you are planning to contribute to the Lumigator backend
codebase.

## Setup

You can deploy and develop Lumigator locally using Docker Compose. Start by running the following
command:

```console
user@host:~/lumigator$ make local-up
```

This creates three container services networked together to make up all the components of the
Lumigator application:

- `localstack`: :ocal storage for datasets that mimics S3-API compatible functionality.
- `backend`: Lumigator’s FastAPI REST API.
- `ray`: a Ray cluster for submitting lm-buddy jobs and serving Ray Serve.

The `local-up` make target will also set a watch on the backend codebase, so that any changes you
make to the codebase will be automatically reflected in the running backend service (see
[here](../../../.devcontainer/docker-compose.override.yaml)). Moreover, it will mount the `local.db`
database file to the backend service, so that any changes you make to the database will be
persisted between runs.

To use the API-based vendor ground truth generation and evaluation, you'll need to pass the
following environment variables for credentials, into the docker container:

- `MISTRAL_API_KEY`: You Mistal API key.
- `OPENAI_API_KEY`: Your OpenAI API key.

## Testing the services

You can test your local setup as follows:

- `SQLite`: Connect to your database with any SQL client that supports SQLite
  (e.g., [DBeaver](https://dbeaver.io/)).
 - `localstack`: Test your localstack setup as follows:
   - Install `s5smd`, a very fast S3 and local filesystem execution tool, by running:
     ```bash
     brew install peak/tap/s5cmd
     ```
   - Export the folowing environment variables:
     ```bash
     export AWS_ACCESS_KEY_ID=test
     export AWS_SECRET_ACCESS_KEY=test
     export AWS_DEFAULT_REGION=us-east-2
     export AWS_ENDPOINT_URL=http://localhost:4566
     ```
    - Set the following alias for convenience:
      ```bash
      alias s5='s5cmd --endpoint-url $AWS_ENDPOINT_URL'
      ```
    - Check out the storage: `s5 ls`
    - Check out the lumigator bucket: `s5 ls s3://lumigator-storage`.
    - Check out the localstack image documentation [here](https://docs.localstack.cloud/references/configuration/).
 - `backend`: Connect to Lumigator's [OpenAPI spec at localhost](http://localhost/docs#), see the
   available endpoints, and interactively run commands.
 - `ray`: Connect to Ray's dashboard [via HTTP to this address](http://localhost:8265/), see the
   cluster status, running jobs, their logs, etc.

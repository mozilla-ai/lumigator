# Local Development

This guide will walk you through setting up a local development environment for Lumigator backend.
This is useful for testing changes to the backend codebase during development or for debugging
issues. Reading this guide is a must if you are planning to contribute to the Lumigator backend
codebase.

## Backend Setup

You can deploy and develop Lumigator locally using Docker Compose. Start by running the following
command:

```console
user@host:~/lumigator$ make local-up
```

This creates four container services networked together to make up all the components of the
Lumigator application:

- `minio`: Local storage for datasets that mimics S3-API compatible functionality.
- `backend`: Lumigator’s FastAPI REST API.
- `ray`: A Ray cluster for submitting several types of jobs.
- `frontend`: Lumigator's Web UI

The `local-up` make target will also set a watch on the backend codebase, so that any changes you
make to the codebase will be automatically reflected in the running backend service (see
[here](../../../.devcontainer/docker-compose.override.yaml)). Moreover, it will mount the `local.db`
database file to the backend service, so that any changes you make to the database will be
persisted between runs.

To use the API-based vendor ground truth generation and evaluation, you'll need to pass the
following environment variables for credentials, into the docker container:

- `MISTRAL_API_KEY`: your Mistral API key.
- `OPENAI_API_KEY`: your OpenAI API key.

Refer to the [troubleshooting section](../get-started/troubleshooting.md) for more details.

## Testing the backend services

You can test your local setup as follows:

- `SQLite`: Connect to your database with any SQL client that supports SQLite
  (e.g., [DBeaver](https://dbeaver.io/)).
- `minio`: Test your minio setup as follows:
    - connect to http://localhost:9001
    - log in with `username=lumigator` and `password=lumigator` (you can customize them in your `.env` file)
    - check out the `lumigator-storage` bucket
- `minio` via command line:
    - install the aws cli: `brew install awscli`
    - export the following environment variables:
      ```bash
      export AWS_ENDPOINT_URL=http://localhost:9000
      export AWS_ACCESS_KEY_ID=lumigator
      export AWS_SECRET_ACCESS_KEY=lumigator
      ```
    - Check out the lumigator bucket: `aws s3 ls s3://lumigator-storage`.
 - `backend`: Connect to Lumigator's [OpenAPI spec at localhost](http://localhost/docs#), see the
   available endpoints, and interactively run commands.
 - `ray`: Connect to Ray's dashboard [via HTTP to this address](http://localhost:8265/), see the
   cluster status, running jobs, their logs, etc.

## Frontend Setup

This guide can be used to build and run the Lumigator frontend (UI) for development or production environments.

### Prerequisites

Ensure you have the following installed on your system:

- **Node.js** (version 14 or higher)
- **npm** or **yarn** package manager

### Installation

1. **Clone the repository** (if you haven't already):

   Using HTTPS:

   ```console
   user@host:~$ git clone https://github.com/mozilla-ai/lumigator.git
   ```

   Or using SSH:

   ```console
   user@host:~$ git@github.com:mozilla-ai/lumigator.git
   ```

1. Navigate to the `lumigator/frontend` directory:

   ```console
   user@host:~$ cd lumigator/lumigator/frontend
   ```

1. **Install dependencies**:

   Using npm:

   ```console
   user@host:~/lumigator/lumigator/frontend$ npm install
   ```

   Or using yarn:

   ```console
   user@host:~/lumigator/lumigator/frontend$ yarn install
   ```

### Development

To run the frontend locally for development purposes, use the following command to start the Vite development server. This will also enable hot-reloading, so changes you make in the code will be reflected instantly in the browser.

```console
user@host:~/lumigator/lumigator/frontend$ npm run dev
```

Or using yarn:

```console
user@host:~/lumigator/lumigator/frontend$ yarn dev
```

Visit `http://localhost` in your browser. The application runs at this address by default.

### Build for Production

To build the frontend for production, run:

```console
user@host:~/lumigator/lumigator/frontend$ npm run build
```

This command will bundle the frontend code into a production-ready, optimized set of static assets located in the `dist` directory. By default `dist` is placed in project's root directory ( `./lumigator/frontend` in this case).

### Linting and Code Formatting

For consistent code formatting and linting across multiple contributors, ESLint and Prettier are configured. To run linting:

```console
user@host:~/lumigator/lumigator/frontend$ npm run lint
```

To fix linting issues automatically:

```console
user@host:~/lumigator/lumigator/frontend$ npm run lint:fix
```


### Debugging with VSCode and DebugPy

The backend and unit tests can be debugged with VsCode using Debugpy. If you're not familiar with how debugging python in vscode works, we recommend you read VSCode's documentation [here](https://code.visualstudio.com/docs/python/debugging). When running the command `make local-up`, the backend automatically creates the debugpy listener, which you can attach to using the `Attach to Backend` Debug configuration present in the `.vscode/launch.json` file of this repo.

Similarly, the unit tests can be debugged by adding the parameter `DEBUGPY=true` when running a make test command. For example, `make test-sdk-unit DEBUGPY=true` will run the test with the debugger and you can attach using the `Attach to Tests` Debug configuration. Note that with this enabled, the unit tests wait for you to attach the debugger before running any tests.

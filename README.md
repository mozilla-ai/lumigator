# Mozilla.ai Lumigator 🐊

[![Lumigator pipeline](https://github.com/mozilla-ai/lumigator/actions/workflows/lumigator_pipeline.yaml/badge.svg?branch=main)](https://github.com/mozilla-ai/lumigator/actions/workflows/lumigator_pipeline.yaml)
[![Docs](https://github.com/mozilla-ai/lumigator/actions/workflows/build_and_publish_docs.yaml/badge.svg)](https://github.com/mozilla-ai/lumigator/actions/workflows/build_and_publish_docs.yaml)

Lumigator is an open-source platform developed by [Mozilla.ai](https://www.mozilla.ai/) to help
users select the most suitable language model for their specific needs. Currently, Lumigator
supports the evaluation of summarization tasks using sequence-to-sequence models such as BART, as well as causal models like GPT and Mistral. We plan to expand support to additional machine
learning tasks and use cases in the future.

To learn more about Lumigator's features and capabilities, see the
[documentation](https://mozilla-ai.github.io/lumigator/), or get started with the
[example notebook](/notebooks/walkthrough.ipynb) for a platform API walkthrough.

> [!NOTE]
> Lumigator is in the early stages of development. It is missing important features and
> documentation. You should expect breaking changes in the core interfaces and configuration
> structures as development continues.

## Why Lumigator?

As more organizations turn to AI for solutions, they face the challenge of selecting the best model
from an ever-growing list of options. The AI landscape is evolving rapidly, with [twice as many new
models released in 2023 compared to the previous year](https://hai.stanford.edu/research/ai-index-report).
However, in spite of existing [benchmarks and leaderboards](https://crfm.stanford.edu/helm/classic/latest/#/leaderboard) for some scenarios, one may find it challenging to compare models for their specific domain and use case.

[The 2024 AI Index Report](https://arxiv.org/pdf/2405.19522)
highlighted that AI evaluation tools aren’t (yet) keeping up with the pace of development, making it
harder for developers and businesses to make informed choices. Without a clear method for
comparing models, many teams end up using suboptimal solutions, or just choosing models based on
hype, slowing down product progress and innovation.

With Lumigator MVP, Mozilla.ai aims to make model selection transparent, efficient, and empowering.
Lumigator provides a framework for comparing LLMs, using task-specific metrics to evaluate how well
a model fits your project’s needs. With Lumigator, we want to ensure that you’re not just picking a
model—you’re picking the right model for your use case.

## Get started

The simplest way to set up Lumigator is to deploy it locally using Docker Compose. To this end, you
need to have the following prerequisites installed on your machine:

- A working installation of [Docker](https://docs.docker.com/engine/install/).
    - On a Mac, you need Docker Desktop `4.3` or later and docker-compose `1.28` or later.
    - On Linux, you need to follow the
      [post-installation steps](https://docs.docker.com/engine/install/linux-postinstall/).
- The system Python (version managers such as uv should be deactivated)
- At least 10 GB available on disk and allocated for docker, since some small language models will be pre downloaded

You can run and develop Lumigator locally using Docker Compose. This creates four container
services networked together to make up all the components of the Lumigator application:

- `minio`: Local storage for datasets that mimics S3-API compatible functionality.
- `backend`: Lumigator’s FastAPI REST API.
- `ray`: A Ray cluster for submitting several types of jobs.
- `frontend`: Lumigator's Web UI

> [!NOTE]
> Lumigator requires an SQL database to hold metadata for datasets and jobs. The local deployment
> uses SQLite for this purpose.

> [!NOTE]
If you want to evaluate against LLM APIs like OpenAI and Mistral, you need to set the appropriate
environment variables: `OPENAI_API_KEY` or `MISTRAL_API_KEY`. Refer to the
[troubleshooting section](https://mozilla-ai.github.io/lumigator/get-started/troubleshooting.html#tokens-api-keys-not-set)
in our documentation for more details.

To start Lumigator locally, follow these steps:

1. Clone the Lumigator repository:

    ```bash
    git clone git@github.com:mozilla-ai/lumigator.git
    ```

1. Navigate to the repository root directory:

    ```bash
    cd lumigator
    ```

1. If your system has an NVIDIA GPU, you have an additional pre-requirement: [install the NVIDIA Container Toolkit following their instructions](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html). After that, open a terminal and run:
    ```bash
    export RAY_WORKER_GPUS=1
    export RAY_WORKER_GPUS_FRACTION=1.0
    export GPU_COUNT=1
    ```
    **Important: Continue the next steps in this same terminal.**


1. If you intend to use Mistral API or OpenAI API, use that same terminal and run:
    ```bash
    export MISTRAL_API_KEY=your_mistral_api_key
    export OPENAI_API_KEY=your_openai_api_key
    ```
    **Important: Continue the next steps in this same terminal.**

1. From that same terminal, start Lumigator with:

    ```bash
    make start-lumigator
    ```

The last command uses Docker Compose to launch all necessary containers for you.
To verify that Lumigator is running, open a web browser and navigate to
[`http://localhost`](http://localhost): you should see Lumigator's UI.

Now that Lumigator is running, you can start using it. The platform provides a REST API that allows
you to interact with the system. Run the [example notebook](/notebooks/walkthrough.ipynb) for a
quick walkthrough.

Despite the fact this is a local setup, it lends itself to more distributed scenarios. For instance,
one could provide different `AWS_*` environment variables to the backend container to connect to any
provider’s S3-compatible service, instead of minio. Similarly, one could provide a different
`RAY_HEAD_NODE_HOST` to move compute to a remote ray cluster, and so on. See the
[operational guides](https://mozilla-ai.github.io/lumigator/operations-guide/kubernetes.html) in the
documentation for more deployment options.

If you want to permanently set any of the environment variables above, you can  add them to your rc file (e.g. `~/.bashrc`, `~/.zshrc`) or directly to the
`.env` file that is automatically created after the first execution of lumigator.

### Lumigator UI
Alternatively, you can also use the UI to interact with Lumigator. Once a Lumigator session is up and running, the UI can be accessed by visiting [`http://localhost`](http://localhost). On the **Datasets** tab, first upload a csv data with columns `examples` and (optionally) `ground_truth`. Next, the dataset can be used to run an evaluation using the **Experiments** tab.

### Terminate Lumigator session
To stop the containers you started using Docker Compose, simply run the following command:

```bash
make stop-lumigator
```

## Kubernetes Installation

You can also deploy Lumigator on Kubernetes using our [Helm](lumigator/infra/mzai/helm/lumigator) chart.

## Documentation

For the complete Lumigator documentation, visit the
[docs page](https://mozilla-ai.github.io/lumigator).

## Contribute

For contribution guidelines, see the [CONTRIBUTING.md](CONTRIBUTING.md) file.

## Questions? Problems? Suggestions?

To report a bug or request a feature, please open a
[GitHub issue](https://github.com/mozilla-ai/lumigator/issues/new/choose). Be sure to check if
someone else has already created an issue for the same topic.

# Troubleshooting

This section describes some common issues and how you can solve them.
If the problem you are experiencing is not listed here, feel free to
[browse the list of open issues](https://github.com/mozilla-ai/lumigator/issues)
to check if it has already been discussed or otherwise open a
[bug report](https://github.com/mozilla-ai/lumigator/issues/new?template=bug_report.yaml).

## Could not install packages due to an OSError: [Errno 28] No space left on device

This problem usually occurs when the disk space allocated by Docker is completely
filled up. There are two ways to tackle this:

- increase the amount of disk space avaiable to the docker engine. You can do it
by opening Settings in Docker Desktop, opening the `Resources` section, and then
increasing the value specified under `Disk usage limit`

- you can remove the Docker images left dangling by our build process by running the
`docker image prune` command on the command line.


## Tokens / API keys not set

Some models or APIs require a key or a token to work. This may result in different
kind of errors while trying to run jobs that make use of them. For instance, this
happens when you try to run inference using Mistral and `MISTRAL_API_KEY` is not set:

```
  File "/tmp/ray/session_2025-01-23_02-13-26_636661_1/runtime_resources/working_dir_files/_ray_pkg_58d1ff7936232bdd/model_clients.py", line 130, in __init__
    self._client = MistralClient(api_key=os.environ["MISTRAL_API_KEY"])
                                         ~~~~~~~~~~^^^^^^^^^^^^^^^^^^^
  File "<frozen os>", line 679, in __getitem__
KeyError: 'MISTRAL_API_KEY'
```

This happens instead when you try to run inference with OpenAI models and you have
not set `OPENAI_API_KEY`:

```
  File "/tmp/ray/session_2025-01-23_02-18-27_051519_1/runtime_resources/pip/617697551215d8488f42ccab087d2364573ba842/virtualenv/lib/python3.11/site-packages/openai/_client.py", line 105, in __init__
    raise OpenAIError(
openai.OpenAIError: The api_key client option must be set either by passing api_key to the client or by setting the OPENAI_API_KEY environment variable
```

The following, instead, happens when you try to access a model from a gated repository
on HuggingFace without authorizing it or without sharing a `HF_TOKEN`:

```
  File "/tmp/ray/session_2025-01-23_02-18-27_051519_1/runtime_resources/pip/b9beac6aa077c93a8e0edf25e6f0e4c96432df34/virtualenv/lib/python3.11/site-packages/transformers/utils/hub.py", line 420, in cached_file
    raise EnvironmentError(
OSError: You are trying to access a gated repo.
Make sure to have access to it at https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.3.
401 Client Error. (Request ID: Root=1-6792187d-76df0eae4be65d2a47c68d48;8789d12e-a496-4af8-99ce-3b29bbdf5032)

Cannot access gated repo for url https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.3/resolve/main/config.json.
Access to model mistralai/Mistral-7B-Instruct-v0.3 is restricted. You must have access to it and be authenticated to access it. Please log in.
```

To fix any of these, you should:

1. Get the respective key/token (instructions for
[Mistral API](https://docs.mistral.ai/getting-started/quickstart/),
OpenAI API (see `https://platform.openai.com/docs/quickstart`),
[HF gated models](https://huggingface.co/docs/hub/models-gated) and
[tokens](https://huggingface.co/docs/hub/en/security-tokens#how-to-manage-user-access-tokens)
)

2. Save it in your environment, either by adding it into your `~/.bashrc`, `~/.zshrc` file
or by adding it to the `.env` file inside lumigator's main directory

# Mozilla.ai Lumigator

Lumigator is an open-source platform built by [Mozilla.ai](https://www.mozilla.ai/) for guiding users through the process of selecting the right LLM for their needs.

# Setup

Install pants, tools, and dev environment.
This includes a standalone python interpreter, venv (`mzaivenv`), precommit configs, and more. Python setup is
handled by `uv`; pants maintains lockfiles for different platforms. Currently, only `python 3.11.9` is valid for this project; if a compatible interpreter
is found `uv` will not download a standalone python interpreter for you.

For VSCode users, activate the venv before opening your IDE; the `.env` file will be recognized automatically.


```shell
make bootstrap-dev-environment
```

Show targets:

```bash
make show-pants-targets
```

run the app locally via docker compose:

```bash
make local-up
make local-logs # gets the logs from docker compose
make local-down # shuts it down
```

Compile targets manually:

```bash
pants package <target>
# backend app
pants package lumigator/python/mzai/backend --no-local-cache
# backend docker image
pants package lumigator/python/mzai/backend:backend_image
```


## Rebuilding dependencies

You may need to manually regenerate the [lockfiles](https://www.pantsbuild.org/2.21/docs/python/overview/lockfiles) if you update dependencies.
To do so:

1. Add your new dependency to `3rdparty/python/pyproject.toml`. This file respects system platform markers, and only very special cases need to be added as explicit `python_requirement` targets.
2. run `pants generate-lockfiles`. This will take a while - 5-10 minutes in some cases and require access to pypi.

make sure to add the new lockfiles to the repo with your PR. You'll have to rebuild your dev environment if you haven't already.


## Testing the development setup

Using a container, run the following from the root of this repo:


```bash
make test-dev-setup

```

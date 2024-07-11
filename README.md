# Mozilla.ai Lumigator
<<<<<<< HEAD
=======

Source code for the Mozilla.ai Lumigator, a platfrom guiding LLM developers through the process of model selection.
>>>>>>> 3748955 (renaming to Lumigator)

Lumigator is an open-source platform built by [Mozilla.ai](https://www.mozilla.ai/) for guiding users through the process of selecting the right LLM for their needs.

# Setup

Install pants, tools, dev environment.
This includes a standalone python interpreter, venv (`dist/export/python/virtualenvs/python_default/3.11.9/bin/activate`), precommit configs, and more.

For VSCode users, activate the venv before opening your IDE; the `.env` file will be recognized automatically.


```shell
make bootstrap-dev-env
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


## 3rdparty dependencies

You may need to manually regenerate the lockfile [Pants recommends using](https://www.pantsbuild.org/2.21/docs/python/overview/lockfiles) if you update dependencies.
To do so:

<<<<<<< HEAD
1. Add your new dependency to `platform/3rdparty/python/pyproject.toml`. This file respects system platform markers, and only very special cases need to be added as explicit `python_requirement` targets.
2. `pants generate-lockfiles`
=======
1. Add your new dependency to `lumigator/3rdparty/python/pyproject.toml`
2. `pants generate-lockfiles --resolve=python_default`
3. `pants package lumigator/python/mzai/backend`
>>>>>>> 3748955 (renaming to Lumigator)

make sure to add the new lockfiles to the repo with your PR. You'll have to rebuild your dev environment if you haven't already.


## Testing the development setup

Using a container, run the following from the root of this repo:


```bash
<<<<<<< HEAD
make test-dev-setup

=======
# startup
pants run lumigator:docker_compose_up
# shutdown
pants run lumigator:docker_compose_down
>>>>>>> 3748955 (renaming to Lumigator)
```

This will build docker-compose locally. To develop, bring up docker-compose, then open VSCode and it should prompt you to open in devcontainers.

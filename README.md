# MZAI Platform

Source code for the MZAI model builder platform.


# Setup

Install pants + dependencies:

```shell
brew install pantsbuild/tap/pants jq
pants --version  # start the daemon
```

Setup:

Will download a standalone interpreter for python.
```bash
make bootstrap-python
```

Code style is enforced using the [ruff](https://github.com/astral-sh/ruff) linter
and a series of [pre-commit](https://pre-commit.com/) hooks. You can install them locally via:

```
pre-commit install --config ".pre-commit-config.yaml"
```

Show targets:

```bash
make show-pants-targets
```

Compile targets manually:

```bash
pants package <target>
# backend app
pants package platform/python/mzai/backend --no-local-cache
# backend docker image
pants package platform/python/mzai/backend:backend_image
```

Export a venv for your IDE:

```bash
make ide-roots # Sets PYTHONPATH for first-party directories in a .env file
make ide-venv
```

For VSCode users, should activate the venv before opening your IDE
and it should be recognized automatically.


## Rebuilding dependencies

You may need to manually regenrate the lockfile [Pants recommends using](https://www.pantsbuild.org/2.21/docs/python/overview/lockfiles) if you update dependencies.
To do so:

1. Add your new dependency to `platform/3rdparty/python/pyproject.toml`
2. `pants generate-lockfiles --resolve=python_default`
3. `pants package platform/python/mzai/backend`

And check to make sure your new dependency is included


## Running locally with Docker Compose and devcontainers

cd to the root directory

```bash
# builds the docker images assuming M2 arm architecture
make up-arm 
# shutdown
make down 
# logs to see startup errors
make logs
```

This will build docker-compose locally. To develop, bring up docker-compose, then open VSCode and it should prompt you to open in devcontainers. 

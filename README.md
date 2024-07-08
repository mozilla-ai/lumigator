# MZAI Platform

Source code for the MZAI model builder platform.


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

make local-down # shuts it down
```

Compile targets manually:

```bash
pants package <target>
# backend app
pants package platform/python/mzai/backend --no-local-cache
# backend docker image
pants package platform/python/mzai/backend:backend_image
```


## 3rdparty dependencies

You may need to manually regenerate the lockfile [Pants recommends using](https://www.pantsbuild.org/2.21/docs/python/overview/lockfiles) if you update dependencies.
To do so:

1. Add your new dependency to `platform/3rdparty/python/pyproject.toml`. This file respects system platform markers, and only very special cases need to be added as explicit `python_requirement` targets.
2. `pants generate-lockfiles`

make sure to add the new lockfiles to the repo with your PR. You'll have to rebuild your dev environment if you haven't already.


## Testing the development setup

Using a container, run the following from the root of this repo:


```bash
make test-dev-setup
```

This will build docker-compose locally. To develop, bring up docker-compose, then open VSCode and it should prompt you to open in devcontainers. 



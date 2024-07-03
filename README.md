# MZAI Platform

Source code for the MZAI model builder platform.


# Setup

Install pants, tools, dev environment.
This includes a standalone python interpreter, venv (`mzaivenv`), precommit configs, and more.

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


## Rebuilding dependencies

You may need to manually regenerate the lockfile [Pants recommends using](https://www.pantsbuild.org/2.21/docs/python/overview/lockfiles) if you update dependencies.
To do so:

1. Add your new dependency to `platform/3rdparty/python/pyproject.toml`
2. `pants generate-lockfiles --resolve=python_default`
3. `pants package platform/python/mzai/backend`

And check to make sure your new dependency is included.

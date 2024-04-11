# MZAI Platform

Source code for the MZAI model builder platform.


# Setup 

Install pants:

```shell
brew install pantsbuild/tap/pants
pants --version  # start the daemon
```

Setup:

```bash
cat ./pants_tools/macosx_14_pex_platform_tags.json | jq '.path = "'$(which python)'"' > ./pants_tools/macosx_14_pex_platform_tags.json
```

Show targets:

```bash
make show-all-major-targets
```

Compile targets manually:

```bash
pants package <target>
pants package model_builder/python/mzai/backend
# docker image
pants package model_builder/python/mzai/backend:model_builder_image
```

Export a venv for your IDE:

```bash
make pants-roots # Sets PYTHONPATH for first-party directories in a .env file
make ide-venv
```

For VSCode users, should activate the venv before opening your IDE
and it should be recognized automatically.

## Running locally with Docker Compose via pants

```bash
# startup
pants run model_builder:mzai_backend_up
# shutdown
pants run model_builder:mzai_backend_down
```





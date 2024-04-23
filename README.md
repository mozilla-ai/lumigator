# MZAI Platform

Source code for the MZAI model builder platform.


# Setup 

Install pants:

```shell
brew install pantsbuild/tap/pants
pants --version  # start the daemon
```

Setup:

Will download a standalone interpreter for python.
```bash
make bootstrap-python
```

Show targets:

```bash
make show-all-major-targets
```

Compile targets manually:

```bash
pants package <target>
# backend app
pants package platform/python/mzai/backend
# backend docker image
pants package platform/python/mzai/backend:backend_image
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
pants run platform:docker_compose_up
# shutdown
pants run platform:docker_compose_down
```





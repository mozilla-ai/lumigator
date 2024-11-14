# Lumigator SDK

The SDK provides the communication and validation primitives needed to contact the Lumigator itself,
either locally or remotely.

You can install the lumigator SDK  via `pip` directly or via `uv`:

```bash
pip install lumigator-sdk
```

or 

```bash
uv pip install lumigator-sdk
```

Now that you have the SDK installed, you can use it to communicate with Lumigator. You can run the
[example notebook](/notebooks/walkthrough.ipynb) for a platform API walkthrough, or follow the
[quickstart guide](https://mozilla-ai.github.io/lumigator/get-started/quickstart.html) in the
documentation.

## Test instructions

The SDK contains both unit tests (requiring no additional containers) and integration tests (requiring a live Lumigator backend). By default only unit tests are run.

To run unit tests, please use:

```bash
uv run pytest
```

To run integration tests, please use:

```bash
pushd ../../../../ # go back to the project root
make start-lumigator-build # wait until all containers are up and running
popd
uv run pytest -o python_files="int_test_*.py" # wait until all tests have passed; update and repeat...
pushd ../../../../ # go back to the project root
make local-down # wait until all containers are removed
popd
```
# Integration Tests

This folder houses tests that bring together the local package code 
and external job dependencies.
Currently, the main external dependencies of the package are a Ray cluster
and tracking services (e.g., W&B).

## Ray compute

A Ray cluster is provided for testing as a `pytest` fixture (see `conftest.py`).
Currently, this is a tiny cluster with a fixed number of CPUs that runs on
the local test runner machine.
The [Ray documentation](https://docs.ray.io/en/latest/ray-core/examples/testing-tips.html)
provides helpful guides on how to set these clusters up for testing.

## Tracking services

Weights & Biases is currently used as the main experiment tracking service.
For testing, W&B can be disabled by setting the environment variable `WANDB_MODE="offline"`,
which is done automatically in a fixture for integration tests.
This causes the [W&B SDK to act like a no-op](https://docs.wandb.ai/guides/technical-faq/general#can-i-disable-wandb-when-testing-my-code)
so the actual service is not contacted during testing.

However, when W&B is disabled, the loading and logging of artifacts is also disabled
which breaks the input/output data flow for the job entrypoints.
To work around this during testing, we use the `FakeArtifactLoader` class
that stores artifacts in in-memory storage to avoid calls to the W&B SDK.
This allows the full job entrypoints to be executed
and the output artifacts produced by the jobs to be verified as test assertions.

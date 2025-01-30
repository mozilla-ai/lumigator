# Integration Tests

This directory houses tests that bring together the local package code and external job
dependencies. Currently, the main external dependencies of the package is a Ray cluster.

## Ray compute

A Ray cluster is provided for testing as a `pytest` fixture (see `conftest.py`). Currently, this is
a tiny cluster with a fixed number of CPUs that runs on the local test runner machine. The
[Ray documentation](https://docs.ray.io/en/latest/ray-contribute/testing-tips.html) provides helpful
guides on how to set these clusters up for testing.

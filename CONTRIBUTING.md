# Contributing

Lumigator is still in early stages of development and as such will have 
large variance between even PATCH versions in terms of feature development. 
While we're in this phase, we're accepting PRs for clarification in documentation. 

## Project structure

The lumigator project contains several packages: the `lumigator/python/mzai/backend` package that powers the lumigator server functionality, the `lumigator/python/mzai/schemas` package containing the formal schemas for communication with the server through the REST API, and the `lumigator/python/mzai/sdk` package abstracting the REST API for Python applications. Each package holds its own `pyproject.toml` definition.
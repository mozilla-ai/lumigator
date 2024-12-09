# Contributing

Lumigator is still in early stages of development and as such will have
large variance between even PATCH versions in terms of feature development.

We want to encourage both suggestions and contributions from the community in the near future. Before submitting a PR, please open a discussion in a related issue.

The lumigator project contains several packages: the `lumigator/python/mzai/backend` package that powers the lumigator server functionality, the `lumigator/python/mzai/schemas` package containing the formal schemas for communication with the server through the REST API, and the `lumigator/python/mzai/sdk` package abstracting the REST API for Python applications. Each package holds its own `pyproject.toml` definition.

Currently, we are able to accept:

* PRs for [**bugfixes**](https://github.com/mozilla-ai/lumigator/issues/new?assignees=&labels=bug&projects=&template=bug_report.md&title=%5BBUG%5D+) and **documentation** only. Please include as much information as possible;
* [Suggestions](https://github.com/mozilla-ai/lumigator/issues/new?assignees=&labels=&projects=&template=feature_request.md&title=) on making Lumigator easier to understand and contribute to.

# Where to go

* [Lumigator documentation](https://mozilla-ai.github.io/lumigator/): Describes all the components and includes usage guides.
* [Open issues](https://github.com/mozilla-ai/lumigator/issues): Browse the open issues to check if the topic you want to raise is already being discussed.
[Contribute](https://github.com/mozilla-ai/lumigator/contribute): Explore the list of "good first issues" to start contributing.

# SDK release steps

When applying a semver tag version starting with 'v' without pre-release or build sections (e.g. `v0.0.0`), the SDK and schemas publishing process to PyPI will start. The CI actions will check that the existing versions in the corresponding `pyproject.toml` files match the git tag used. For example, a git tag of `v0.1.2` requires a line of `version = 0.1.2` within the `pyproject.toml` file under the `project` table.

The process to prepare a release should be:

* Ensure that the right version is selected.
  * This is kept as a manual step, since versions can be skipped for a number of reasons.
* Fill in this same version in the `lumigator/python/mzai/schemas/pyproject.toml` and `lumigator/python/mzai/sdk/pyproject.toml` files.
* Make a local commit.
* Tag the local commit: `git tag vX.Y.Z`
* Push the local commit: `git push`
* Push the local tag: `git push origin tag vX.Y.Z`

The publishing CI action should then trigger. If this action fails, repeat with a new patch version. Tags should not be moved in the repo to avoid inconsistencies with PyPI package versions.

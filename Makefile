.PHONY: build config up down

ci-setup:
	pants --version  # Bootstrap Pants.

ci-lint: ci-setup
	pants --changed-since=origin/main \
	update-build-files --check \
	lint

ci-fmt: ci-lint
	pants --changed-since=origin/main fmt

ci-tests:
	pants test ::

show-all-major-targets::
	@echo "------shell_command targets-------"
	pants --filter-target-type=shell_command list ::
	pants --filter-target-type=run_shell_command list ::
	@echo "------docker image targets-------"
	pants --filter-target-type=docker_image list ::
	@echo "------python targets-------"
	pants --filter-target-type=python_distribution list ::
	pants --filter-target-type=pex_binary list ::

	@echo "------archive targets-------"

	pants --filter-target-type=archive list ::

	@echo "this is not an exhaustive list, just a convienience."


ide-venv:
	pants export --resolve=python-default

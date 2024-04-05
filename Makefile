DOCKER_DIR=src/infra/docker
COMPOSE_FILE=${DOCKER_DIR}/docker-compose.yaml
ENV_FILE=${DOCKER_DIR}/.env.local

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


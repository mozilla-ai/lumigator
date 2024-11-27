.PHONY: local-up local-down local-logs clean-docker-buildcache clean-docker-images clean-docker-containers start-lumigator-external-services start-lumigator stop-lumigator test sdk-test sdk-unit-test sdk-integration-test-exec sdk-integration-test backend-test backend-unit-test backend-integration-test

SHELL:=/bin/bash
UNAME:= $(shell uname -o)

#used in docker-compose to choose the right Ray image
ARCH := $(shell uname -m)
RAY_ARCH_SUFFIX :=

ifeq ($(ARCH), arm64)
	RAY_ARCH_SUFFIX := -aarch64
endif

LOCAL_DOCKERCOMPOSE_FILE:= docker-compose.yaml
DEV_DOCKER_COMPOSE_FILE:= .devcontainer/docker-compose.override.yaml

.env:
	@if [ ! -f .env ]; then cp .env.example .env; echo ".env created from .env.example"; fi

# Launches Lumigator in 'development' mode (all services running locally, code mounted in)
local-up: .env
	uv run pre-commit install
	RAY_ARCH_SUFFIX=$(RAY_ARCH_SUFFIX) docker compose --profile local -f $(LOCAL_DOCKERCOMPOSE_FILE) -f ${DEV_DOCKER_COMPOSE_FILE} up --watch --build

local-down:
	docker compose --profile local -f $(LOCAL_DOCKERCOMPOSE_FILE) down

local-logs:
	docker compose -f $(LOCAL_DOCKERCOMPOSE_FILE) logs

# Launches lumigator in 'user-local' mode (All services running locally, using latest docker container, no code mounted in)
start-lumigator: .env
	RAY_ARCH_SUFFIX=$(RAY_ARCH_SUFFIX) docker compose --profile local -f $(LOCAL_DOCKERCOMPOSE_FILE) up -d

# Launches lumigator with no code mounted in, and forces build of containers (used in CI for integration tests)
start-lumigator-build: .env
	RAY_ARCH_SUFFIX=$(RAY_ARCH_SUFFIX) docker compose --profile local-fe -f $(LOCAL_DOCKERCOMPOSE_FILE) up -d --build

# Launches lumigator without local dependencies (ray, S3)
start-lumigator-external-services: .env
	docker compose -f $(LOCAL_DOCKERCOMPOSE_FILE) up -d

stop-lumigator:
	RAY_ARCH_SUFFIX=$(RAY_ARCH_SUFFIX) docker compose --profile local --profile local-fe -f $(LOCAL_DOCKERCOMPOSE_FILE) down

clean-docker-buildcache:
	docker builder prune --all -f

clean-docker-containers:
	docker rm -vf $$(docker container ls -aq)

clean-docker-images:
	docker rmi -f $$(docker image ls -aq)

clean-docker-all: clean-docker-containers clean-docker-buildcache clean-docker-images

clean-all: clean-docker-buildcache clean-docker-containers

sdk-unit-test:
	cd lumigator/python/mzai/sdk/tests;	uv run pytest -o python_files="unit/*/test_*.py unit/test_*.py"

sdk-integration-test-exec:
	cd lumigator/python/mzai/sdk/tests; uv run pytest -o python_files="integration/test_*.py integration/*/test_*.py"

sdk-integration-test: | start-lumigator-build sdk-integration-test-exec stop-lumigator

sdk-test: sdk-unit-test sdk-integration-test

backend-unit-test:
	cd lumigator/python/mzai/backend/backend/tests; SQLALCHEMY_DATABASE_URL=sqlite:///local.db uv run pytest -o python_files="backend/tests/unit/*/test_*.py"

backend-integration-test-exec:
	cd lumigator/python/mzai/backend/backend/tests;	SQLALCHEMY_DATABASE_URL=sqlite:///local.db uv run pytest -o python_files="backend/tests/integration/*/test_*.py"

backend-integration-test: | start-lumigator-build backend-integration-test-exec stop-lumigator

backend-test: backend-unit-test backend-integration-test

test: sdk-test backend-test

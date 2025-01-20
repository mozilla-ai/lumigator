.PHONY: local-up local-down local-logs clean-docker-buildcache clean-docker-images clean-docker-containers start-lumigator-external-services start-lumigator stop-lumigator test-sdk-unit test-sdk-integration test-sdk-integration-containers test-sdk test-backend-unit test-backend-integration test-backend-integration-containers test-backend test-jobs-evaluation-unit test-jobs-inference-unit test-jobs test-all check-dot-env

SHELL:=/bin/bash
UNAME:= $(shell uname -o)
PROJECT_ROOT := $(shell git rev-parse --show-toplevel)
CONTAINERS_RUNNING := $(shell docker ps -q --filter "name=lumigator-")

KEEP_CONTAINERS_UP := $(shell grep -E '^KEEP_CONTAINERS_UP=' .env | cut -d'=' -f2 | tr -d '"' || echo "FALSE")

# used in docker-compose to choose the right Ray image
ARCH := $(shell uname -m)
RAY_ARCH_SUFFIX :=
COMPUTE_TYPE := -cpu
RAY_WORKER_GPUS ?= 0
RAY_WORKER_GPUS_FRACTION ?= 0.0
GPU_COMPOSE :=

$(info RAY_WORKER_GPUS = $(RAY_WORKER_GPUS))

ifeq ($(ARCH), arm64)
	RAY_ARCH_SUFFIX := -aarch64
endif

ifeq ($(shell test $(RAY_WORKER_GPUS) -ge 1; echo $$?) , 0)
	COMPUTE_TYPE := -gpu
	GPU_COMPOSE := -f docker-compose.gpu.override.yaml
endif

# lumigator runs on a set of containers (backend, ray, minio, etc).
# The following allows one to start all of them before calling a target
# (typically a test), run the target, then pull everything down afterwards.
# When testing, one can set the KEEP_CONTAINERS_UP env var to "TRUE"
# so they can check logs from the running containers.
define run_with_containers
	@echo "No Lumigator containers are running. Starting containers..."
	make start-lumigator-build
	@if [ $(KEEP_CONTAINERS_UP) = "FALSE" ]; then echo "The script will remove containers after tests"; trap "cd $(PROJECT_ROOT); make stop-lumigator" EXIT; fi; \
	make $(1)
endef

# `run_with_existing_containers` allows one to run a target (typically
# a test) on already running containers.
define run_with_existing_containers
	@echo "Lumigator containers are already running."
	@if [ -n "$(AUTO_TEST_RUN)" ]; then \
		echo "AUTO_TEST_RUN is set to '$(AUTO_TEST_RUN)'"; \
		case "$(AUTO_TEST_RUN)" in \
			[Yy]* ) \
				echo "Running tests..."; \
				make $(1); \
				;; \
			[Nn]* ) \
				echo "Tests aborted due to AUTO_TEST_RUN setting."; \
				exit 1; \
				;; \
			* ) \
				echo "Invalid AUTO_TEST_RUN value: $(AUTO_TEST_RUN). Tests aborted."; \
				exit 1; \
				;; \
		esac; \
	else \
		read -p "Do you want to run tests with the current Lumigator deployment? (Y/n): " choice; \
		case $${choice:-Y} in \
			[Yy]* ) \
				echo "Running tests..."; \
				make $(1); \
				;; \
			[Nn]* ) \
				echo "Tests aborted."; \
				exit 1; \
				;; \
			* ) \
				echo "Invalid input. Tests aborted."; \
				exit 1; \
				;; \
		esac; \
	fi
endef

LOCAL_DOCKERCOMPOSE_FILE:= docker-compose.yaml
DEV_DOCKER_COMPOSE_FILE:= .devcontainer/docker-compose.override.yaml

check-dot-env:
	@if [ ! -f .env ]; then cp .env.template .env; echo ".env created from .env.template"; fi

# Launches Lumigator in 'development' mode (all services running locally, code mounted in)
local-up: check-dot-env
	uv run pre-commit install
	RAY_ARCH_SUFFIX=$(RAY_ARCH_SUFFIX) COMPUTE_TYPE=$(COMPUTE_TYPE) docker compose --profile local $(GPU_COMPOSE) -f $(LOCAL_DOCKERCOMPOSE_FILE) -f ${DEV_DOCKER_COMPOSE_FILE} up --watch --build

local-down:
	docker compose --profile local -f $(LOCAL_DOCKERCOMPOSE_FILE) down

local-logs:
	docker compose -f $(LOCAL_DOCKERCOMPOSE_FILE) logs

# Launches lumigator in 'user-local' mode (All services running locally, using latest docker container, no code mounted in)
start-lumigator: check-dot-env
	RAY_ARCH_SUFFIX=$(RAY_ARCH_SUFFIX) COMPUTE_TYPE=$(COMPUTE_TYPE) docker compose --profile local $(GPU_COMPOSE) -f $(LOCAL_DOCKERCOMPOSE_FILE) up -d

# Launches lumigator with no code mounted in, and forces build of containers (used in CI for integration tests)
start-lumigator-build: check-dot-env
	RAY_ARCH_SUFFIX=$(RAY_ARCH_SUFFIX) COMPUTE_TYPE=$(COMPUTE_TYPE) docker compose --profile local $(GPU_COMPOSE) -f $(LOCAL_DOCKERCOMPOSE_FILE) up -d --build

# Launches lumigator without local dependencies (ray, S3)
start-lumigator-external-services: check-dot-env
	docker compose $(GPU_COMPOSE) -f $(LOCAL_DOCKERCOMPOSE_FILE) up -d

stop-lumigator:
	RAY_ARCH_SUFFIX=$(RAY_ARCH_SUFFIX) COMPUTE_TYPE=$(COMPUTE_TYPE) docker compose --profile local $(GPU_COMPOSE) -f $(LOCAL_DOCKERCOMPOSE_FILE) down

clean-docker-buildcache:
	docker builder prune --all -f

clean-docker-containers:
	docker container prune

# remove all dangling images + all mzdotai/* ones
clean-docker-images:
	docker images "mzdotai/*" -q | xargs -n1 docker rmi -f; \
	docker image prune

clean-docker-all: clean-docker-containers clean-docker-buildcache clean-docker-images

clean-all: clean-docker-buildcache clean-docker-containers


# SDK tests
# We have both unit and integration tests for the SDK.
# Integration tests require all containers to be up, so as a safety measure
# `test-sdk-integration-containers` is usually called and this will either
# start them if they are not present or use the currently running ones.
test-sdk-unit:
	cd lumigator/python/mzai/sdk/tests; \
	uv run pytest -o python_files="unit/*/test_*.py unit/test_*.py"

test-sdk-integration:
	cd lumigator/python/mzai/sdk/tests; \
	uv run pytest -s -o python_files="integration/test_*.py integration/*/test_*.py"

test-sdk-integration-containers:
ifeq ($(CONTAINERS_RUNNING),)
	$(call run_with_containers, test-sdk-integration)
else
	$(call run_with_existing_containers, test-sdk-integration)
endif

test-sdk: test-sdk-unit test-sdk-integration-containers


# backend tests
# We have both unit and integration tests for the backend.
# Integration tests require all containers to be up, so as a safety measure
# `test-sdk-integration-containers` is usually called and this will either
# start them if they are not present or use the currently running ones.
test-backend-unit:
	cd lumigator/python/mzai/backend/; \
	S3_BUCKET=lumigator-storage \
	RAY_HEAD_NODE_HOST=localhost \
	RAY_DASHBOARD_PORT=8265 \
	SQLALCHEMY_DATABASE_URL=sqlite:////tmp/local.db \
	uv run pytest -o python_files="backend/tests/unit/*/test_*.py"

test-backend-integration:
	cd lumigator/python/mzai/backend/; \
	docker container list --all; \
	S3_BUCKET=lumigator-storage \
	RAY_HEAD_NODE_HOST=localhost \
	RAY_DASHBOARD_PORT=8265 \
	SQLALCHEMY_DATABASE_URL=sqlite:////tmp/local.db \
	RAY_WORKER_GPUS="0.0" \
	RAY_WORKER_GPUS_FRACTION="0.0" \
	INFERENCE_PIP_REQS=../jobs/inference/requirements_cpu.txt \
	INFERENCE_WORK_DIR=../jobs/inference \
	EVALUATOR_PIP_REQS=../jobs/evaluator/requirements.txt \
	EVALUATOR_WORK_DIR=../jobs/evaluator \
	EVALUATOR_LITE_PIP_REQS=../jobs/evaluator_lite/requirements.txt \
	EVALUATOR_LITE_WORK_DIR=../jobs/evaluator_lite \
	uv run pytest -s -o python_files="backend/tests/integration/*/test_*.py"

test-backend-integration-containers:
ifeq ($(CONTAINERS_RUNNING),)
	$(call run_with_containers, test-backend-integration)
else
	$(call run_with_existing_containers, test-backend-integration)
endif

test-backend: test-backend-unit test-backend-integration-containers


# jobs tests
# We only have unit tests for jobs. They do not require any container to
# be running, but they will set up a different, volatile python environment
# with all the deps specified in their respective `requirements.txt` files.
test-jobs-evaluation-unit:
	cd lumigator/python/mzai/jobs/evaluator_lite; \
	uv run --with pytest --with-requirements requirements.txt --isolated pytest

test-jobs-inference-unit:
	cd lumigator/python/mzai/jobs/inference; \
	uv run --with pytest --with-requirements requirements.txt --isolated pytest

test-jobs-unit: test-jobs-evaluation-unit test-jobs-inference-unit


# test everything
test-all: test-sdk test-backend test-jobs-unit

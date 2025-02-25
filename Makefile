.PHONY: local-up local-down local-logs clean-docker-buildcache clean-docker-images clean-docker-containers start-lumigator-external-services start-lumigator start-lumigator-postgres stop-lumigator test-sdk-unit test-sdk-integration test-sdk-integration-containers test-sdk test-backend-unit test-backend-integration test-backend-integration-containers test-backend test-jobs-evaluation-unit test-jobs-inference-unit test-jobs test-all config-clean config-generate-env setup config-generate-key

SHELL:=/bin/bash
UNAME:= $(shell uname -o)

# Required binaries in order to correctly run the makefile, if any cannot be found the script will fail.
# uv is only required for local-up (dev).
REQUIRED_BINARIES := git docker openssl
$(foreach bin,$(REQUIRED_BINARIES),\
  $(if $(shell command -v $(bin) 2> /dev/null),,$(error Please install `$(bin)`)))

PROJECT_ROOT := $(shell git rev-parse --show-toplevel)
CONTAINERS_RUNNING := $(shell docker ps -q --filter "name=lumigator-")

KEEP_CONTAINERS_UP ?= "FALSE"

# Configuration to identify the input and output config files
# NOTE: Changing CONFIG_BUILD_DIR will require review of .gitignore
CONFIG_BUILD_DIR=$(shell pwd)/build
# Path to default config prefixed with dot to hide from user
CONFIG_DEFAULT_FILE:=$(shell pwd)/.default.conf
# Directory for user specific configuration and keys
CONFIG_USER_DIR:=${HOME}/.lumigator
# Path to user editable config file (will be generated if missing)
CONFIG_OVERRIDE_FILE:=$(CONFIG_USER_DIR)/user.conf
# Location of the key to use for encryption.
CONFIG_USER_KEY_FILE:=$(CONFIG_USER_DIR)/lumigator.key
# Env var name to hold encryption key
CONFIG_USER_KEY_ENV_VAR=LUMIGATOR_SECRET_KEY

# used in docker-compose to choose the right Ray image
ARCH := $(shell uname -m)
RAY_ARCH_SUFFIX :=
COMPUTE_TYPE := -cpu
RAY_WORKER_GPUS ?= 0
RAY_WORKER_GPUS_FRACTION ?= 0.0
GPU_COMPOSE :=
SQLALCHEMY_DATABASE_URL ?= sqlite:////tmp/local.db

DEBUGPY_ARGS :=
ifneq ($(shell echo $(DEBUGPY) | grep -i '^true$$'),)
    DEBUGPY_ARGS := -m debugpy --listen 5679 --wait-for-client
endif

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
POSTGRES_DOCKER_COMPOSE_FILE:= .devcontainer/docker-compose-postgres.override.yaml

define remove_config_dir
	@echo "Cleaning up temporary config directory: '$(CONFIG_BUILD_DIR)'..."
	@rm -rf $(CONFIG_BUILD_DIR)
	@echo "Cleanup complete"
endef

# Launches Lumigator in 'development' mode (all services running locally, code mounted in)
local-up: config-generate-env
	uv run pre-commit install
	RAY_ARCH_SUFFIX=$(RAY_ARCH_SUFFIX) COMPUTE_TYPE=$(COMPUTE_TYPE) docker compose --env-file "$(CONFIG_BUILD_DIR)/.env" --profile local $(GPU_COMPOSE) -f $(LOCAL_DOCKERCOMPOSE_FILE) -f $(DEV_DOCKER_COMPOSE_FILE) up --watch --build

local-down: config-generate-env
	docker compose --env-file "$(CONFIG_BUILD_DIR)/.env" --profile local $(GPU_COMPOSE) -f $(LOCAL_DOCKERCOMPOSE_FILE) -f ${DEV_DOCKER_COMPOSE_FILE} down
	$(call remove_config_dir)

local-logs:
	docker compose -f $(LOCAL_DOCKERCOMPOSE_FILE) logs

# Launches lumigator in 'user-local' mode (All services running locally, using latest docker container, no code mounted in) - postgres version
start-lumigator-postgres: config-generate-env
	RAY_ARCH_SUFFIX=$(RAY_ARCH_SUFFIX) COMPUTE_TYPE=$(COMPUTE_TYPE) docker compose --env-file "$(CONFIG_BUILD_DIR)/.env" --profile local $(GPU_COMPOSE) -f $(LOCAL_DOCKERCOMPOSE_FILE) -f $(POSTGRES_DOCKER_COMPOSE_FILE) up -d

# Launches lumigator in 'user-local' mode (All services running locally, using latest docker container, no code mounted in)
start-lumigator: config-generate-env
	RAY_ARCH_SUFFIX=$(RAY_ARCH_SUFFIX) COMPUTE_TYPE=$(COMPUTE_TYPE) docker compose --env-file "$(CONFIG_BUILD_DIR)/.env" --profile local $(GPU_COMPOSE) -f $(LOCAL_DOCKERCOMPOSE_FILE) up -d

# Launches lumigator with no code mounted in, and forces build of containers (used in CI for integration tests)
start-lumigator-build: config-generate-env
	RAY_ARCH_SUFFIX=$(RAY_ARCH_SUFFIX) COMPUTE_TYPE=$(COMPUTE_TYPE) docker compose --env-file "$(CONFIG_BUILD_DIR)/.env" --profile local $(GPU_COMPOSE) -f $(LOCAL_DOCKERCOMPOSE_FILE) up -d --build

# Launches lumigator with no code mounted in, and forces build of containers (used in CI for integration tests)
start-lumigator-build-postgres: config-generate-env
	RAY_ARCH_SUFFIX=$(RAY_ARCH_SUFFIX) COMPUTE_TYPE=$(COMPUTE_TYPE) docker compose --env-file "$(CONFIG_BUILD_DIR)/.env" --profile local $(GPU_COMPOSE) -f $(LOCAL_DOCKERCOMPOSE_FILE) -f $(POSTGRES_DOCKER_COMPOSE_FILE) up -d --build

# Launches lumigator without local dependencies (ray, S3)
start-lumigator-external-services: config-generate-env
	docker compose --env-file "$(CONFIG_BUILD_DIR)/.env"$(GPU_COMPOSE) -f $(LOCAL_DOCKERCOMPOSE_FILE) up -d

stop-lumigator: config-generate-env
	RAY_ARCH_SUFFIX=$(RAY_ARCH_SUFFIX) COMPUTE_TYPE=$(COMPUTE_TYPE) docker compose --env-file "$(CONFIG_BUILD_DIR)/.env" --profile local $(GPU_COMPOSE) -f $(LOCAL_DOCKERCOMPOSE_FILE) -f $(POSTGRES_DOCKER_COMPOSE_FILE) down
	$(call remove_config_dir)

clean-docker-buildcache:
	docker builder prune --all -f

clean-docker-containers:
	docker container prune --filter label=ai.mozilla.product_name=lumigator

# remove all dangling images + all mzdotai/* ones
clean-docker-images:
	docker images "mzdotai/*" -q | xargs -n1 docker rmi -f; \
	docker image prune

clean-docker-all: clean-docker-containers clean-docker-buildcache clean-docker-images

clean-all: clean-docker-buildcache clean-docker-containers config-clean

setup:
	@scripts/setup_uv.sh;

# This target is used to update the OpenAPI docs for use in the sphinx docs.
# Lumigator must be running on localhost
update-openapi-docs:
	./scripts/update_openapi_docs.sh

# This target is used to check the OpenAPI docs in the running lumigator vs the existing sphinx docs.
# Lumigator must be running on localhost
check-openapi-docs:
	./scripts/check_openapi_docs.sh

# SDK tests
# We have both unit and integration tests for the SDK.
# Integration tests require all containers to be up, so as a safety measure
# `test-sdk-integration-containers` is usually called and this will either
# start them if they are not present or use the currently running ones.
test-sdk-unit:
	cd lumigator/sdk/tests; \
	uv run $(DEBUGPY_ARGS) -m pytest -o python_files="unit/*/test_*.py unit/test_*.py"

test-sdk-integration:
	cd lumigator/sdk/tests; \
	uv run $(DEBUGPY_ARGS) -m pytest -s -o python_files="integration/test_*.py integration/*/test_*.py"

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
	cd lumigator/backend/; \
	S3_BUCKET=lumigator-storage \
	RAY_HEAD_NODE_HOST=localhost \
	RAY_DASHBOARD_PORT=8265 \
	SQLALCHEMY_DATABASE_URL=sqlite:////tmp/local.db \
	MLFLOW_TRACKING_URI=http://localhost:8001 \
	PYTHONPATH=../jobs:$$PYTHONPATH \
	LUMIGATOR_SECRET_KEY=7yz2E+qwV3TCg4xHTlvXcYIO3PdifFkd1urv2F/u/5o= \
	uv run $(DEBUGPY_ARGS) -m pytest -s -o python_files="backend/tests/unit/*/test_*.py backend/tests/unit/test_*.py" # pragma: allowlist secret

test-backend-integration:
	cd lumigator/backend/; \
	docker container list --all; \
	S3_BUCKET=lumigator-storage \
	RAY_HEAD_NODE_HOST=localhost \
	RAY_DASHBOARD_PORT=8265 \
	MLFLOW_TRACKING_URI=http://localhost:8001 \
	SQLALCHEMY_DATABASE_URL=$(SQLALCHEMY_DATABASE_URL) \
	RAY_WORKER_GPUS="0.0" \
	RAY_WORKER_GPUS_FRACTION="0.0" \
	INFERENCE_PIP_REQS=../jobs/inference/requirements_cpu.txt \
	INFERENCE_WORK_DIR=../jobs/inference \
	EVALUATOR_PIP_REQS=../jobs/evaluator/requirements.txt \
	EVALUATOR_WORK_DIR=../jobs/evaluator \
	PYTHONPATH=../jobs:$$PYTHONPATH \
	LUMIGATOR_SECRET_KEY=7yz2E+qwV3TCg4xHTlvXcYIO3PdifFkd1urv2F/u/5o= \
	uv run $(DEBUGPY_ARGS) -m pytest -s -o python_files="backend/tests/integration/*/test_*.py" # pragma: allowlist secret

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
	cd lumigator/jobs/evaluator; \
	uv run $(DEBUGPY_ARGS) --with pytest --with-requirements requirements.txt --isolated pytest

test-jobs-inference-unit:
	cd lumigator/jobs/inference; \
	uv run $(DEBUGPY_ARGS) --with pytest --with-requirements requirements.txt --isolated pytest

test-jobs-unit: test-jobs-evaluation-unit test-jobs-inference-unit


# test everything
test-all: test-sdk test-backend test-jobs-unit

# config-clean: removes any generated config files from the build directory (including the directory itself).
config-clean:
	$(call remove_config_dir)

# config-generate-env: parses a generated config YAML file and outputs a .env file ready for use in Docker.
config-generate-env: config-clean config-generate-key
	@scripts/config_generate_env.sh "$(CONFIG_BUILD_DIR)" "$(CONFIG_USER_KEY_FILE)" "$(CONFIG_USER_KEY_ENV_VAR)" "$(CONFIG_DEFAULT_FILE)" "$(CONFIG_OVERRIDE_FILE)"

# config-generate-key: ensures that a (new or existing) user owned secret key exists to be passed to lumigator and used for encryption.
config-generate-key:
	@scripts/config_generate_key.sh $(CONFIG_USER_DIR) $(CONFIG_USER_KEY_FILE)

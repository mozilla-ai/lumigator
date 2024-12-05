.PHONY: local-up local-down local-logs clean-docker-buildcache clean-docker-images clean-docker-containers start-lumigator-external-services start-lumigator stop-lumigator test-sdk-unit test-sdk-integration test-sdk-integration-target test-sdk-target test-backend-unit test-backend-integration test-backend-integration-target test-backend-target test-all-target test-%

SHELL:=/bin/bash
UNAME:= $(shell uname -o)
PROJECT_ROOT := $(shell git rev-parse --show-toplevel)
CONTAINERS_RUNNING := $(shell docker ps -q --filter "name=lumigator-")

#used in docker-compose to choose the right Ray image
ARCH := $(shell uname -m)
RAY_ARCH_SUFFIX :=

ifeq ($(ARCH), arm64)
	RAY_ARCH_SUFFIX := -aarch64
endif

define run_with_containers
	@echo "No Lumigator containers are running. Starting containers..."
	make start-lumigator-build
	trap "cd $(PROJECT_ROOT); make stop-lumigator" EXIT; \
	make $(1)
endef

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
	RAY_ARCH_SUFFIX=$(RAY_ARCH_SUFFIX) docker compose --profile local-fe -f $(LOCAL_DOCKERCOMPOSE_FILE) up -d

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

test-sdk-unit:
	cd lumigator/python/mzai/sdk/tests; \
	uv run pytest -o python_files="unit/*/test_*.py unit/test_*.py"

test-sdk-integration-target:
	cd lumigator/python/mzai/sdk/tests; \
	uv run pytest -o python_files="integration/test_*.py integration/*/test_*.py"

test-sdk-integration:
ifeq ($(CONTAINERS_RUNNING),)
	$(call run_with_containers, test-sdk-integration-target)
else
	$(call run_with_existing_containers, test-sdk-integration-target)
endif

test-backend-unit:
	cd lumigator/python/mzai/backend/; \
	rm local.db; \
	SQLALCHEMY_DATABASE_URL=sqlite:///local.db uv run pytest -o python_files="backend/tests/unit/*/test_*.py"

test-backend-integration-target:
	cd lumigator/python/mzai/backend/; \
	rm local.db; \
	SQLALCHEMY_DATABASE_URL=sqlite:///local.db RAY_WORKER_GPUS="0.0" RAY_WORKER_GPUS_FRACTION="0.0" INFERENCE_PIP_REQS=../jobs/inference/requirements.txt INFERENCE_WORK_DIR=../jobs/inference EVALUATOR_PIP_REQS=../jobs/evaluator/requirements.txt EVALUATOR_WORK_DIR=../jobs/evaluator uv run pytest -o python_files="backend/tests/integration/*/test_*.py"

test-backend-integration:
ifeq ($(CONTAINERS_RUNNING),)
	$(call run_with_containers, test-backend-integration-target)
else
	$(call run_with_existing_containers, test-backend-integration-target)
endif

test-sdk-target: test-sdk-unit test-sdk-integration

test-backend-target: test-backend-unit test-backend-integration

test-all-target: test-sdk-target test-backend-target

# Check whether there are already running containers before starting tests:
#   If so, ask user if they want to proceed with the current deployment.
#   If not: (1) start containers, (2) run tests, (3) tear down containers
#   (regardless of tests outcome).
test-%:
	$(MAKE) test-$*-target

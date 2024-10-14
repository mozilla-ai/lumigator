.PHONY: ci-setup ci-lint ci-fmt ci-tests show-pants-targets clean-python local-up local-down local-logs install-pants bootstrap-python clean-docker-buildcache clean-docker-images clean-docker-containers clean-pants install-uv bootstrap-dev-environment

SHELL:=/bin/bash
UNAME:= $(shell uname -o)
PY_VERSION := 3.11.9
CUDA_AVAILABLE := $(shell nvidia-smi &> /dev/null; echo $$?)
PANTS_INSTALLED := $(shell pants --version &> /dev/null; echo $$?)
PYTHON :=
#used in docker-compose to choose the right Ray image
ARCH := $(shell uname -m)
RAY_ARCH_SUFFIX :=
PYTHON_INSTALL_DIR:=.python

ifeq ($(ARCH), arm64)
	RAY_ARCH_SUFFIX := -aarch64
endif

ifndef PYTHON
	ifeq ($(UNAME), GNU/Linux)
		# UV's installation path post /opt/python
		PYTHON := $(PYTHON_INSTALL_DIR)/cpython-${PY_VERSION}-linux-x86_64-gnu/bin/python3
		ifeq ($(CUDA_AVAILABLE), 0)
			PARAMETRIZE := linux_cuda
		else
			PARAMETRIZE = linux_cpu
		endif
	else
		PYTHON := $(PYTHON_INSTALL_DIR)/cpython-${PY_VERSION}-macos-aarch64-none/bin/python3
		PARAMETRIZE := darwin
	endif
export UV_PYTHON_INSTALL_DIR = $(PYTHON_INSTALL_DIR)
endif


VENV:= mzaivenv/bin/activate

######### developer (mostly) setup targets ##########
print_my_env:
	echo $$UV_PYTHON_INSTALL_DIR

install-pants:
ifneq ($(PANTS_INSTALLED),0)
	bash pants_tools/get-pants.sh
endif


$(PYTHON):
	@echo "Installing python and configuring venv"
	bash devtools/shell/bootstrap_python.sh

$(VENV): $(PYTHON)

bootstrap-python: $(PYTHON) $(VENV)

.env: $(PYTHON) install-pants
	# From: https://www.pantsbuild.org/2.20/docs/using-pants/setting-up-an-ide
	# ROOTS="$(shell pants roots)" $(PYTHON) -c "print('PYTHONPATH=./' + ':./'.join('''$$ROOTS'''.strip().split(' ')) + ':\$$PYTHONPATH')" > .env
	$(PYTHON) -c "print('PYTHONPATH=./' + ':./'.join('''$(shell pants roots)'''.strip().split(' ')) + ':\$$PYTHONPATH')" > .env

bootstrap-dev-environment: $(PYTHON) $(VENVNAME) install-pants  .env


update-3rdparty-lockfiles:
### use this target when you add a new dependency to 3rdparty or change versions of a dep.
	pants generate-lockfiles

###### Local app development workflow. Allows for using
# devcontainer in `.devcontainer` via local docker compose.
# local-up and down are the main targets, and will expect that
# `bootstrap-dev-environment` has been ran, but no need to make it
# specifically dependent on that step.

LOCAL_DOCKERCOMPOSE_FILE:= docker-compose.yaml
DEV_DOCKER_COMPOSE_FILE:= .devcontainer/docker-compose.override.yaml

local-up: 
	RAY_ARCH_SUFFIX=$(RAY_ARCH_SUFFIX) docker compose -f $(LOCAL_DOCKERCOMPOSE_FILE) -f ${DEV_DOCKER_COMPOSE_FILE} up -d --build


local-down:
	docker compose -f $(LOCAL_DOCKERCOMPOSE_FILE) down

local-logs:
	docker compose -f $(LOCAL_DOCKERCOMPOSE_FILE) logs


start-lumigator:
	RAY_ARCH_SUFFIX=$(RAY_ARCH_SUFFIX) docker compose -f $(LOCAL_DOCKERCOMPOSE_FILE) up -d 

stop-lumigator:
	RAY_ARCH_SUFFIX=$(RAY_ARCH_SUFFIX) docker compose -f $(LOCAL_DOCKERCOMPOSE_FILE) down
######
# convenience function that mostly shows the various targets in this repo. not necessary at all
######
show-pants-targets:
	@echo "------shell_command targets-------"
	pants --filter-target-type=shell_command list ::
	pants --filter-target-type=run_shell_command list ::

	@echo "------docker_image targets-------"
	pants --filter-target-type=docker_image list ::

	@echo "------python targets-------"
	pants --filter-target-type=python_distribution list ::
	pants --filter-target-type=pex_binary list ::

	@echo "------archive targets-------"
	pants --filter-target-type=archive list ::

	@echo "this is not an exhaustive list, just a convenience."


######### CLEANERS ###########
clean-python-venv:
	rm -rf mzaivenv/
	rm -rf dist/export/python/

clean-python: clean-python-venv
	rm -rf .python/

clean-pants:
	# this level of clean removes the -build artifacts that pants makes. it doesn't remove the pants cache.
	rm -rf ./dist/

clean-pants-cache: clean-pants
	@echo 'removing the cache dir at $HOME/.cache/pants'
	rm -rf $(HOME)/.cache/pants
	@echo 'resetting the pants daemon:'
	pants --no-pantsd --version
	@echo 'removed the basic cache; if you see issues like:'
	@echo '#############'
	@echo "IntrinsicError: Could not identify a process to backtrack to for: Missing digest: Was not present in the local store"
	@echo '#############'
	@echo "run the following as a potential fix, then re-run your command again."
	@echo 'PANTS_LOCAL_STORE_DIR=$$(mktemp -d) pants lint ::'
	@echo '#############'

clean-docker-buildcache:
	docker builder prune --all -f

clean-docker-containers:
	docker rm -vf $$(docker container ls -aq)

clean-docker-images:
	docker rmi -f $$(docker image ls -aq)

clean-docker-all: clean-docker-containers clean-docker-buildcache clean-docker-images

clean-all: clean-pants-cache clean-docker-buildcache clean-docker-containers



########## CI targets #################

ci-setup:
	pants --version  # Bootstrap Pants.

ci-lint: ci-setup
	# this target uses git to sort out only running on changes since the last main.
	pants --changed-since=origin/main \
	update-build-files --check \
	lint

ci-fmt: ci-lint
	pants --changed-since=origin/main fmt

ci-tests:
	@echo "running tests with parametrized platform: $(PARAMETRIZE)"
	pants test lumigator/python/mzai/backend/backend/tests:backend_tests@parametrize=$(PARAMETRIZE)
	pants test lumigator/python/mzai/sdk/tests:sdk_tests@parametrize=$(PARAMETRIZE)

ci-publish-images:
	pants package publish lumigator/python/mzai/backend:lumigator

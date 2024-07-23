.PHONY: ci-setup ci-lint ci-fmt ci-tests show-pants-targets clean-python local-up local-down local-logs install-pants bootstrap-python clean-docker-buildcache clean-docker-images clean-docker-containers clean-pants

VENVNAME:= mzaivenv
SHELL:=/bin/bash
UNAME:= $(shell uname -o)

ifeq ($(UNAME), GNU/Linux)
	PY_PATH:= /opt/python/install/bin
	PYTHON:= /opt/python/install/bin/python3.11
	PY_DEPS:= 3rdparty/python/requirements_python_linux.txt
endif

ifeq ($(UNAME), Darwin)
	PY_PATH:= .python/python3.11.9/python/install/bin
	PYTHON:= .python/python3.11.9/python/install/bin/python3.11
	PY_DEPS:= 3rdparty/python/requirements_python_darwin.txt
endif


######### developer (mostly) setup targets ##########
PANTS_INSTALLED := $(shell pants --version 1>&2 2> /dev/null; echo $$?)

install-pants:
ifneq ($(PANTS_INSTALLED),0)
	bash pants_tools/get-pants.sh
endif
ifeq ($(UNAME), GNU/Linux)
		pip install uv
endif
ifeq ($(UNAME), Darwin)
		brew install uv
endif

update-3rdparty-lockfiles:
### use this target when you add a new dependency to 3rdparty or change versions of a dep.
	pants generate-lockfiles


$(PYTHON):
	@echo "Installing python and configuring venv"
	# uses python standalone - installs it in the repo by default under `./python`. has
	#  considerations for platform, works on osx and debian / ubuntu linux
	bash pants_tools/bootstrap_python.sh $(UNAME)
	$(PYTHON) -m pip install uv pex

bootstrap-python: $(PYTHON) $(VENVNAME)

$(VENVNAME): $(PYTHON)
	# use uv to create a venv from our lockfile.
	pants run 3rdparty/python:gen_requirements_python_darwin
	$(PYTHON) -m uv venv $(VENVNAME) --seed --python $(PYTHON)
	# $(PYTHON) -m uv pip install --require-hashes --no-cache --strict -r $(PY_DEPS)
	uv pip install --python $(PYTHON) --require-hashes --no-cache --strict -r $(PY_DEPS)
	$(PY_PATH)/pre-commit install --config ".pre-commit-config.yaml"

	echo "To use the environment, please run `source $(VENVNAME)/bin/activate`"

.env: $(PYTHON)
	# From: https://www.pantsbuild.org/2.20/docs/using-pants/setting-up-an-ide
	# ROOTS="$(shell pants roots)" $(PYTHON) -c "print('PYTHONPATH=./' + ':./'.join('''$$ROOTS'''.strip().split(' ')) + ':\$$PYTHONPATH')" > .env
	$(PYTHON) -c "print('PYTHONPATH=./' + ':./'.join('''$(shell pants roots)'''.strip().split(' ')) + ':\$$PYTHONPATH')" > .env

bootstrap-dev-environment: $(PYTHON) $(VENVNAME) install-pants  .env

###### Local app development workflow. Allows for using
# devcontainer in `.devcontainer` via local docker compose.
# local-up and down are the main targets, and will expect that
# `bootstrap-dev-environment` has been ran, but no need to make it
# specifically dependent on that step.

LOCAL_DOCKERCOMPOSE_FILE:= .devcontainer/docker-compose-local.yaml

local-up:
	pants run 3rdparty/python:gen_requirements_python_linux
	docker compose -f $(LOCAL_DOCKERCOMPOSE_FILE) up -d --build

local-down:
	docker compose -f $(LOCAL_DOCKERCOMPOSE_FILE) down

local-logs:
	docker compose -f $(LOCAL_DOCKERCOMPOSE_FILE) logs



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
	# the following resets the pants daemon
	pants --no-pantsd --version
	@echo 'if you see issues like:'
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

clean-all: clean-more-pants clean-docker-buildcache clean-docker-containers



########## CI targets #################

# the following target is meant to be used for changes made to the platform setup itself
# and tests if we can get the basic install going correctly in a container.
# this is meant to be 'alpha' ish and subject to change; will raise some potential issues
# that are likely bc of mounting the filesystem like this.
# if you get a fresh copy of the repo it works as expected.
test-dev-setup:
	docker run --rm -it \
	  --volume .:/home/workspace/lumigator \
	  --privileged --pid=host \
	  --name devbox \
	  --entrypoint "/bin/bash" \
	  -e PANTS_LOCAL_EXECUTION_ROOT_DIR=/workspace \
	  -e PANTS_LOCAL_CACHE=False \
	  mzdotai/golden:base_latest  \
	  -c 'apt-get install -y jq curl make gh && cd /home/workspace/lumigator && rm -rf dist/* && mkdir -p /root/.cache/pants/ && chmod +w -R /root/ && make clean-python && mkdir -p /root/.cache/pants/lmdb_store && chmod +w -R /root/.cache && make bootstrap-dev-environment'

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
	pants test ::

ci-publish-images:
	pants --filter-target-type=docker_image list lumigator/:: | xargs pants package publish

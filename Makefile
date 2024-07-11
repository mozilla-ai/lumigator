.PHONY: ci-setup ci-lint ci-fmt ci-tests show-pants-targets clean-python local-up local-down local-logs install-pants bootstrap-python clean-docker-buildcache clean-docker-images clean-docker-containers clean-pants

VENVNAME:= dist/export/python/virtualenvs/python_default/3.11.9/bin/activate
SHELL:=/bin/bash
UNAME:= $(shell uname -o)

ifeq ($(UNAME), GNU/Linux)
	PYTHON:= /opt/python/install/bin/python3.11
	PY_DEPS:= platform/3rdparty/python/requirements_linux.txt
endif

ifeq ($(UNAME), Darwin)
	PY_PATH:= .python/python3.11.9/python/install/bin
	PYTHON:= .python/python3.11.9/python/install/bin/python3.11
	PY_DEPS:= platform/3rdparty/python/requirements_darwin.txt
endif



######### developer (mostly) setup targets ##########
PANTS_INSTALLED := $(shell pants --version 1>&2 2> /dev/null; echo $$?)

ci-tests:
	pants --filter-target-type=docker_image list lumigator/::

ci-publish-images:
	pants --filter-target-type=docker_image list lumigator/:: | xargs pants publish


install-pants:
ifneq ($(PANTS_INSTALLED),0)
	bash pants_tools/get-pants.sh
endif

update-3rdparty-lockfiles:
### use this target when you add a new dependency to 3rdparty or change versions of a dep.
	pants generate-lockfiles


$(PYTHON):
	@echo "Installing python and configuring venv"
	# uses python standalone - installs it in the repo by default under `./python`. has
	#  considerations for platform, works on osx and debian / ubuntu linux
	bash pants_tools/bootstrap_python.sh $(UNAME)


$(VENVNAME): $(PYTHON)
	pants export --py-resolve-format=mutable_virtualenv --resolve=python_default
	@echo "To use the environment, please run source $(VENVNAME)"

bootstrap-python: $(VENVNAME)

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

<<<<<<< HEAD
=======
ide-roots:
	# From: https://www.pantsbuild.org/2.18/docs/using-pants/setting-up-an-ide
	$(eval ROOTS=$(shell pants roots))
	python3 -c "print('PYTHONPATH=./' + ':./'.join('''$(ROOTS)'''.strip().split(' ')) + ':\$$PYTHONPATH')" > .env

ide-venv: bootstrap-python
	pants generate-lockfiles
	pants export --py-resolve-format=mutable_virtualenv --resolve=python_default


######### developer setup targets
prep-devcontainer:
	docker pull mzdotai/golden:base_latest
	pants package lumigator/python/mzai/backend:backend_image
	pants package lumigator/python/mzai/jobrunner:ray_jobrunner_image
	@echo "now you can use the devcontainer file in the IDE of your choice"


bootstrap-python:
	# sets up the local python pod for development
	bash pants_tools/bootstrap_python.sh $(PLAT)
	pants package lumigator/python/mzai/backend:backend_image

bootstrap-ide: ide-roots ide-venv


######### CLEANERS ###########
clean-python:
	rm -rf .python/
	rm -rf mzaivenv/
	rm -rf dist/export/python/

clean-pants:
	# this level of clean removes the -build artifacts that pants makes. it doesn't remove the pants cache.
	rm -rf ./dist/

clean-pants-cache: clean-pants
	rm -rf $(HOME)/.cache/pants
	# the following resets the pants daemon
	pants --no-pantsd --version
	@echo 'if you see issues like:'
	@echo "IntrinsicError: Could not identify a process to backtrack to for: Missing digest: Was not present in the local store"
	@echo "run the following as a potential fix, then re-run your command again."
	@echo 'PANTS_LOCAL_STORE_DIR=$$(mktemp -d) pants lint ::'

clean-docker-buildcache:
	docker builder prune --all -f

clean-docker-containers:
	docker rm -vf $$(docker container ls -aq)

clean-docker-images:
	docker rmi -f $$(docker image ls -aq)

clean-docker-all: clean-docker-containers clean-docker-buildcache clean-docker-images

clean-all: clean-more-pants clean-docker-buildcache clean-docker-containers



########## CI targets #################
# only meant to be used in github actions.

# the following target is meant to be used for changes made to the platform setup itself
# and tests if we can get the basic install going correctly in a container.
# this is meant to be 'alpha' ish and subject to change; will raise some potential issues
# that are likely bc of mounting the filesystem like this.
# if you get a fresh copy of the repo it works as expected.
test-dev-setup:
	docker run --rm -it \
	  --volume .:/home/workspace/mzai-platform \
	  --privileged --pid=host \
	  --name devbox \
	  --entrypoint "/bin/bash" \
	  -e PANTS_LOCAL_EXECUTION_ROOT_DIR=/workspace \
	  -e PANTS_LOCAL_CACHE=False \
	  mzdotai/golden:base_latest  \
	  -c 'apt-get install -y jq curl make gh && cd /home/workspace/mzai-platform && rm -rf dist/* && mkdir -p /root/.cache/pants/ && chmod +w -R /root/ && make clean-python && mkdir -p /root/.cache/pants/lmdb_store && chmod +w -R /root/.cache && make bootstrap-dev-environment'

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
	pants --filter-target-type=docker_image list platform/:: | xargs pants package publish

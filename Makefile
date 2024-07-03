.PHONY: ci-setup ci-lint ci-fmt ci-tests show-pants-targets clean-python local-up local-down local-logs install-pants

PLAT:= $(shell uname -o)
PYTHON:= .python/python3.11.9/python/install/bin/python3.11
VENVNAME:= mzaivenv

######### developer (mostly) setup targets ##########

install-pants:
	# TODO - add platform-agnostic setup - this assumes brew and
	brew install pantsbuild/tap/pants uv

update-3rdparty-lockfiles:
### use this target when you add a new dependency to 3rdparty or change versions of a dep.
	pants generate-lockfiles

$(PYTHON):
	# uses python standalone - installs it in the repo by default under `./python`. has
	#  considerations for platform, works on osx and debian / ubuntu linux
	bash pants_tools/bootstrap_python.sh $(PLAT)


$(VENVNAME)/bin/activate: $(PYTHON)
	# pants will export a venv for you to use. combined with the `env` file created above
	# it tells your IDE which paths are python libraries or not and ensures the deps are loaded with your interpreter.
	# pants export --py-resolve-format=mutable_virtualenv --resolve=python_default
	pants run platform/3rdparty/python:make_requirements_file
	uv venv $(VENVNAME) --seed --python $(PYTHON) && \
		source ./$(VENVNAME)/bin/activate && \
		uv pip install --require-hashes --no-deps --no-cache-dir --upgrade -r ./platform/3rdparty/python/requirements.txt

.env: $(PYTHON)
	# From: https://www.pantsbuild.org/2.20/docs/using-pants/setting-up-an-ide
	$(eval ROOTS=$(shell pants roots)) && $(PYTHON) -c "print('PYTHONPATH=./' + ':./'.join('''$(ROOTS)'''.strip().split(' ')) + ':\$$PYTHONPATH')" > .env

bootstrap-dev-environment: install-pants $(PYTHON) $(VENVNAME)/bin/activate .env
	pre-commit install --config ".pre-commit-config.yaml"

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


######### CLEANERS ###########
clean-python:
	rm -rf .python/
	rm -rf mzaivenv/

clean-pants:
	# this level of clean removes the -build artifacts that pants makes. it doesn't remove the pants cache.
	rm -rf ./dist/

clean-more-pants: clean-pants
	# this will remove the default pants cache.
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
	pants --filter-target-type=docker_image list platform/::

ci-publish-images:
	pants --filter-target-type=docker_image list platform/:: | xargs pants publish

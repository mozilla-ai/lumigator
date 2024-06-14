.PHONY: ci-setup ci-lint ci-fmt ci-tests show-pants-targets ide-roots ide-venv bootstrap-python clean-python

PLAT:= $(shell uname -o)


pulumi-setup:
	pulumi login

ci-setup:
	pants --version  # Bootstrap Pants.

ci-lint: ci-setup
	pants --changed-since=origin/main \
	update-build-files --check \
	lint

ci-fmt: ci-lint
	pants --changed-since=origin/main fmt

ci-tests:
	pants --filter-target-type=docker_image list platform/::

ci-publish-images:
	pants --filter-target-type=docker_image list platform/:: | xargs pants publish

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

ide-roots:
	# From: https://www.pantsbuild.org/2.18/docs/using-pants/setting-up-an-ide
	$(eval ROOTS=$(shell pants roots))
	python3 -c "print('PYTHONPATH=./' + ':./'.join('''$(ROOTS)'''.strip().split(' ')) + ':\$$PYTHONPATH')" > .env

ide-venv:
	pants generate-lockfiles
	pants export --py-resolve-format=mutable_virtualenv --resolve=python_default

bootstrap-ide: ide-roots ide-venv

bootstrap-python:
	bash pants_tools/bootstrap_python.sh $(PLAT)

clean-python:
	rm -rf .python/

clean-pants:
	rm -rf ./dist/

clean-more-pants: clean-pants
	rm -rf $(HOME)/.cache/pants
# run once to reset
	pants --no-pantsd --version

clean-docker-buildcache:
	docker builder prune --all -f

clean-docker-containers:
	docker rm -vf $$(docker container ls -aq)

clean-docker-images:
	docker rmi -f $$(docker image ls -aq)

clean-all: clean-more-pants clean-docker-buildcache clean-docker-containers


bootstrap-devenv: bootstrap-python


.PHONY: local-up local-down local-logs clean-docker-buildcache clean-docker-images clean-docker-containers

SHELL:=/bin/bash
UNAME:= $(shell uname -o)

#used in docker-compose to choose the right Ray image
ARCH := $(shell uname -m)
RAY_ARCH_SUFFIX :=

ifeq ($(ARCH), arm64)
	RAY_ARCH_SUFFIX := -aarch64
endif

LOCAL_DOCKERCOMPOSE_FILE:= docker-compose.yaml

local-up:
	RAY_ARCH_SUFFIX=$(RAY_ARCH_SUFFIX) docker compose -f $(LOCAL_DOCKERCOMPOSE_FILE) up -d --build

local-down:
	docker compose -f $(LOCAL_DOCKERCOMPOSE_FILE) down

local-logs:
	docker compose -f $(LOCAL_DOCKERCOMPOSE_FILE) logs

clean-docker-buildcache:
	docker builder prune --all -f

clean-docker-containers:
	docker rm -vf $$(docker container ls -aq)

clean-docker-images:
	docker rmi -f $$(docker image ls -aq)

clean-docker-all: clean-docker-containers clean-docker-buildcache clean-docker-images

clean-all: clean-docker-buildcache clean-docker-containers
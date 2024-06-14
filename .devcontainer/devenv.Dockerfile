#syntax = docker/dockerfile:1.4
# 1.4 allows the nice heredoc style blocks

###
# most of this is copied from the source dockerfile; python is different still and
# i'm happy to use that instead soon; this is mostly to test it here right away.
# it's mostly good to use

###

ARG PY_VERSION="3.11.9"
# the bundle unpacks to `python`, not `python+version`
ARG INSTALL_PATH="/opt/python"
ARG LOCAL_PYTHON_PATH="${INSTALL_PATH}/install/bin"
ARG PY_INTERPRETER="${LOCAL_PYTHON_PATH}/python3"

# this is the image built in source
FROM --platform=linux/amd64  mzdotai/golden:base_latest

ENV PATH="/opt:${PATH}"
ENV PATH="${PY_INTERPRETER}:${PATH}"
ENV PYTHONPATH=${LOCAL_PYTHON_PATH}

RUN mkdir -p -m 0700 ~/.ssh && ssh-keyscan github.com >> ~/.ssh/known_hosts

RUN apt-get install -y coreutils


ENV SCIE_BOOT=bootstrap-tools

RUN mkdir /workspace
WORKDIR /workspace


# requires entrypoint with this particular set of changes.
# breaks with devcontainer, perhaps just devpod, if it's a `CMD`
ENTRYPOINT ["/bin/sh", "-c", "echo Running\nwhile true; do sleep 1; done"]

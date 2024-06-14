#syntax = docker/dockerfile:1.4
# 1.4 allows the nice heredoc style blocks

###
# most of this is copied from the source dockerfile; python is different still and
# i'm happy to use that instead soon; this is mostly to test it here right away.
# it's mostly good to use

###

ARG PY_VERSION="3.10.13"
# the bundle unpacks to `python`, not `python+version`
ARG INSTALL_PATH="/opt/python"
ARG LOCAL_PYTHON_PATH="${INSTALL_PATH}/install/bin"
ARG PY_INTERPRETER="${LOCAL_PYTHON_PATH}/python3"

FROM python:3.10.13-bookworm as build-env


RUN mkdir -p /install_packages
COPY ./pants_tools/get-pants.sh /install_packages
WORKDIR /opt

ENV PATH="/opt:${PATH}"

RUN <<EOF
#!/bin/bash
set -eux
ls /install_packages
bash /install_packages/get-pants.sh -d /opt
EOF





FROM python:3.10.13-bookworm as pybuild-env

ARG PY_VERSION
ARG INSTALL_PATH
ARG LOCAL_PYTHON_PATH
ARG PY_INTERPRETER

RUN mkdir -p /install_packages
COPY *.txt /install_packages

RUN mkdir -p ${INSTALL_PATH}
WORKDIR /opt

RUN <<EOF
#!/bin/bash
set -eux
# this is the release tag - see https://github.com/indygreg/python-build-standalone/releases/
apt update
apt install -y xz-utils zstd
TAG="20240224"  # this is the last tag with 3.10.13
URL="https://github.com/indygreg/python-build-standalone/releases/download/$TAG"
DEBIAN="cpython-${PY_VERSION}+${TAG}-x86_64-unknown-linux-gnu-pgo+lto-full.tar.zst"
wget -nv "$URL/$DEBIAN"
tar -axvf "$DEBIAN"
rm cpython* || true
ln -s $PY_INTERPRETER python3
EOF

ENV PATH="/opt:${LOCAL_PYTHON_PATH}:${PATH}"


FROM debian
ARG PY_VERSION
ARG INSTALL_PATH
ARG LOCAL_PYTHON_PATH
ARG PY_INTERPRETER
COPY --from=pybuild-env /opt /opt

ENV PATH="${LOCAL_PYTHON_PATH}:${PATH}"

RUN <<EOF
apt update
apt install -y software-properties-common
apt-get install -y openssh-client git wget htop ack vim s3cmd xz-utils zstd
EOF


RUN mkdir -p -m 0700 ~/.ssh && ssh-keyscan github.com >> ~/.ssh/known_hosts
ENV SCIE_BOOT=bootstrap-tools
COPY --from=build-env /opt/pants /opt
ENV PATH="/opt:${PATH}"
RUN mkdir /workspace
WORKDIR /workspace
RUN pants --version

CMD ["/bin/sh", "-c", "echo Running\nwhile true; do sleep 1; done"]

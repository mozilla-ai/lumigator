FROM fedora:39

ARG RAY_UID=1000
ARG RAY_GID=100
ARG PYTHON_VERSION=3.9
ARG HOSTTYPE=${HOSTTYPE:-aarch64}

ENV TZ=America/Los_Angeles
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

# This is not is not supported for OCI image format
# If you're building this with podman set `--format docker`:
# $ docker run --format docker ...
SHELL ["/bin/bash", "-c"]

RUN dnf -y update && dnf -y upgrade
RUN dnf -y install \
    sudo \
    tzdata \
    git \
    jemalloc-devel \
    wget \
    cmake \
    g++ \
    zlib-devel \
    libgcc \
    libffi \
    python3-pip \
    python3-devel  # needed to build the wheels for psutil

# Create a `ray` user and add it to sudoers
# On Fedora, it is the `wheel` group the user has to be added to,
# as this group has full admin privileges.
RUN useradd -ms /bin/bash -d /home/ray ray --uid $RAY_UID --gid $RAY_GID
RUN usermod -aG wheel ray && echo 'ray ALL=NOPASSWD: ALL' >> /etc/sudoers

USER $RAY_UID
ENV HOME=/home/ray
WORKDIR $HOME

COPY requirements-constraints.txt requirements-constraints.txt

RUN <<EOF
#!/bin/bash

set -euo pipefail

PIP_PKGS=(setuptools==71.1.0 flatbuffers cython numpy psutil)
pip install --no-cache-dir -c requirements-constraints.txt "${PIP_PKGS[@]}"

EOF

ARG BASE_IMAGE

FROM $BASE_IMAGE

ARG HOSTTYPE=${HOSTTYPE:-aarch64}
ENV PATH "$HOME/.local/bin/:$PATH"

RUN pip install ray[all]

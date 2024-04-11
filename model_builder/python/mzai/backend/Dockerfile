FROM ubuntu:22.04 as base

FROM base as builder
ARG PY_VERSION="3.10"
ARG PY_EXECUTABLE="python${PY_VERSION}"

### install system packages
ENV DEBIAN_FRONTEND=noninteractive

# we need libpq-dev for postgres interaction / building psycopg2
RUN apt-get update \
    && apt-get install -y software-properties-common \
    && apt-get update \
    && add-apt-repository ppa:deadsnakes/ppa \
    && apt-get -y install \
    gcc \
    python3.10-dev \
    libpq-dev \
    curl

### install pip and python packages
RUN curl -sS https://bootstrap.pypa.io/get-pip.py | ${PY_EXECUTABLE}

WORKDIR /app
# model_builder.python.mzai is the output place for the built pex
# it's in `dist/model_builder.python.mzai.backed`
COPY model_builder.python.mzai.backend/backend_app.pex .
RUN export PEX_TOOLS=1

ENTRYPOINT ["python3", "backend_app.pex"]

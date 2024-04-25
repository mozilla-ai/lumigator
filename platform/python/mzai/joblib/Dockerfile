ARG BASE_IMAGE=rayproject/ray:2.9.3.94a6d7-py310

FROM $BASE_IMAGE

WORKDIR /joblib

ENV PEX_TOOLS=1

COPY platform.python.mzai.joblib/joblib_app.pex .

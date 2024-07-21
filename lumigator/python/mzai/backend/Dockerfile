ARG BASE_IMAGE=python:3.11.9-bookworm
FROM $BASE_IMAGE
WORKDIR /app
COPY lumigator.python.mzai.backend/backend_app@parametrize=linux_cpu.pex .
RUN mv 'backend_app@parametrize=linux_cpu.pex' backend_app.pex
ENTRYPOINT ["./backend_app.pex"]

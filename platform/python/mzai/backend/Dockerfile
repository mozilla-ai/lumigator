ARG BASE_IMAGE=python:3.10.13-bookworm
FROM $BASE_IMAGE
WORKDIR /app
COPY platform.python.mzai.backend/backend_app.pex .
ENTRYPOINT ["./backend_app.pex"]

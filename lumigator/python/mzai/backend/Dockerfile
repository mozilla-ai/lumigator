ARG BASE_IMAGE=python:3.11.9-bookworm
FROM $BASE_IMAGE
WORKDIR /app
COPY lumigator.python.mzai.backend/backend_app.pex .
ENTRYPOINT ["./backend_app.pex"]

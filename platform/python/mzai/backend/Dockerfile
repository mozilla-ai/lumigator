ARG BASE_IMAGE="python:3.10"

FROM $BASE_IMAGE

WORKDIR /app

# platform.python.mzai is the output place for the built pex
# it's in `dist/platform.python.mzai.backend`
COPY platform.python.mzai.backend/backend_app.pex .

ENTRYPOINT ["./backend_app.pex"]

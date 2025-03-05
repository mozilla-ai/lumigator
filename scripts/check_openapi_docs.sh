#!/bin/bash

cd lumigator/backend/
export S3_BUCKET=lumigator-storage
export RAY_HEAD_NODE_HOST=localhost
export RAY_DASHBOARD_PORT=8265
export SQLALCHEMY_DATABASE_URL=sqlite:////tmp/local.db
export MLFLOW_TRACKING_URI=http://localhost:8001
export PYTHONPATH=../jobs:$$PYTHONPATH
export LUMIGATOR_SECRET_KEY=7yz2E+qwV3TCg4xHTlvXcYIO3PdifFkd1urv2F/u/5o=
uv run python -m backend.openapi_spec fetched_openapi.json

# Compare normalized OpenAPI JSON (ignoring newline differences)
if ! diff -u <(tr -d '\n' < ../../docs/source/specs/openapi.json) <(tr -d '\n' < fetched_openapi.json); then
  echo "Error: The OpenAPI documentation is outdated. Please update the OpenAPI JSON file."
  exit 1
fi
echo "OpenAPI documentation is up to date."
rm fetched_openapi.json
exit 0

#!/bin/bash

cd lumigator/backend/
export S3_BUCKET=lumigator-storage
export RAY_HEAD_NODE_HOST=localhost
export RAY_DASHBOARD_PORT=8265
export SQLALCHEMY_DATABASE_URL=sqlite:////tmp/local.db
export MLFLOW_TRACKING_URI=http://localhost:8001
export PYTHONPATH=../jobs:$$PYTHONPATH
export LUMIGATOR_SECRET_KEY=7yz2E+qwV3TCg4xHTlvXcYIO3PdifFkd1urv2F/u/5o=
uv run python -m backend.openapi_spec ../../docs/source/specs/openapi.json

#!/bin/bash

REPO_PATH="$HOME/workspace/mzai-platform"
cd "$REPO_PATH"

# docker pull openapijsonschematools/openapi-json-schema-generator-cli
# PYTHONPATH="$REPO_PATH/backend" python backend/src/dump_openapi_schema.py || exit 1

#docker run --rm -v "$REPO_PATH":/local openapijsonschematools/openapi-json-schema-generator-cli \
#    generate \
#    -i /local/backend/openapi.json \
#    -g python \
#    --additional-properties=projectName="mzai-platform-python-sdk" \
#    -o /local/sdk/gen


PYTHONPATH="$REPO_PATH/backend" python backend/src/dump_openapi_schema.py || exit 1




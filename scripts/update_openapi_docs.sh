#!/bin/bash
# cd to the root dir
cd "$(dirname "$0")"/..
# Timeout after 5 minutes (300 seconds)
TIMEOUT=300
START_TIME=$(date +%s)

# Wait for the service to be ready
until curl -sSf http://localhost:8000/openapi.json; do
  echo "Waiting for service to be ready..."
  sleep 5

  CURRENT_TIME=$(date +%s)
  ELAPSED_TIME=$((CURRENT_TIME - START_TIME))

  if [ $ELAPSED_TIME -ge $TIMEOUT ]; then
    echo "Error: Service did not become ready within 5 minutes."
    exit 1
  fi
done

# Fetch OpenAPI JSON
curl -sSf http://localhost:8000/openapi.json -o docs/source/specs/openapi.json

echo "OpenAPI documentation has been updated."
exit 0

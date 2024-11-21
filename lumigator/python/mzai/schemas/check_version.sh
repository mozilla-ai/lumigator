#!/bin/bash
set -eu

PYVERSION=$(uv run yq -p toml -oy ".project.version" pyproject.toml)
TAG=$(git describe --exact-match --tags 2> /dev/null)

if [ "${PYVERSION}" != "${TAG}" ]; then
    echo "Version mismatch - pyproject:${PYVERSION} git:${TAG}"
    exit 1
fi
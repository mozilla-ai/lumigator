#!/bin/bash
set -eu

PYVERSION=$(uv run yq -p toml -oy ".project.version" pyproject.toml)
TAG=$(git describe --exact-match --tags)

if [ "v${PYVERSION}" != "${TAG}" ]; then
    echo "Version mismatch - pyproject:${PYVERSION} git:${TAG}"
    exit 1
fi
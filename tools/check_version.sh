#!/bin/bash
set -eu

PYVERSION=$(yq -p toml -oy ".project.version" pyproject.toml)
TAG=$(git describe --exact-match --tags)

if [ "${PYVERSION}" != "${TAG}" ]; then
    echo "Version mismatch - pyproject:${PYVERSION} git:${TAG}"
    exit 1
fi

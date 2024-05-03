#!/bin/bash
echo "BUILD_TIME $(date +%s)"
echo "STABLE_GIT_COMMIT $(git rev-parse --short HEAD)"
echo "STABLE_USER_NAME $USER"
echo "CURRENT_BRANCH $(git rev-parse --abbrev-ref HEAD)"
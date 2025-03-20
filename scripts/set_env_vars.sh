#!/bin/bash

set -e  # Exit on error

# #######################
# Source common functions
# #######################
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMMON_FILE="$SCRIPT_DIR/common.sh"

if [ -f "$COMMON_FILE" ]; then
    source "$COMMON_FILE"
else
    echo "Error: common.sh not found!" >&2
    exit 1
fi

# Default environment variables
DEFAULT_VARS=(
    AWS_ACCESS_KEY_ID=lumigator
    AWS_SECRET_ACCESS_KEY=lumigator # pragma: allowlist secret
    AWS_DEFAULT_REGION=us-east-2
    AWS_ENDPOINT_URL=http://localhost:9000
    S3_ENDPOINT_URL=http://localhost:9000
    LOCAL_FSSPEC_S3_ENDPOINT_URL=http://localhost:9000
    S3_BUCKET=lumigator-storage
	RAY_HEAD_NODE_HOST=localhost
	RAY_DASHBOARD_PORT=8265
	MLFLOW_TRACKING_URI=http://localhost:8001
	SQLALCHEMY_DATABASE_URL="$SQLALCHEMY_DATABASE_URL"
	RAY_WORKER_GPUS="0.0"
	RAY_WORKER_GPUS_FRACTION="0.0"
	INFERENCE_PIP_REQS=../jobs/inference/requirements_cpu.txt
	INFERENCE_WORK_DIR=../jobs/inference
	EVALUATOR_PIP_REQS=../jobs/evaluator/requirements.txt
	EVALUATOR_WORK_DIR=../jobs/evaluator
	LUMIGATOR_SECRET_KEY=7yz2E+qwV3TCg4xHTlvXcYIO3PdifFkd1urv2F/u/5o=
)

# Function to set environment variables from a file
set_vars_from_file() {
    ENV_VARS_FILE="$1"

    # Check if the file exists and is readable
    if [[ -f "$ENV_VARS_FILE" ]]; then
        while IFS= read -r line; do
            # Remove inline comments and trim spaces
            sanitized_line=$(echo "$line" | sed 's/^\([^#]*=[^#]*\).*/\1/' | xargs)

            # Skip empty lines or lines starting with whitespace followed by #
            [[ -z "$sanitized_line" || "$sanitized_line" =~ ^[[:space:]]*# ]] && continue

            # Split the line into key and value based on the first '=' occurrence
            key="${sanitized_line%%=*}"
            value="${sanitized_line#*=}"

            # Trim spaces from key and value
            key=$(echo "$key" | xargs)
            value=$(echo "$value" | xargs)

            # We only remove any leading and trailing spaces (don't remove quotes)
            if [[ "$value" =~ ^\".*\"$ ]]; then
                value="${value:1:-1}" # Strip quotes but keep the value
            fi

            # If the value is empty, try falling back to the existing env var value
            if [[ -z "$value" && -n "${!key}" ]]; then
                echo_dark_grey "$key -> [FALLBACK] using existing value"
                value="${!key}"
            fi

            # Only export the value if it's a non-empty string (not just quotes)
            if [[ -n "$value" ]]; then
                export "$key"="$value"
                echo_magenta "$key=$value"
            else
                echo_yellow "$key -> [SKIPPED]: value is empty"
            fi

        done < "$ENV_VARS_FILE"
    else
        echo_red "Error: File not found or not readable: $ENV_VARS_FILE"
        exit 1
    fi
}

# Function to set default environment variables
set_default_vars() {
    for line in "${DEFAULT_VARS[@]}"; do
        # Remove inline comments and trim spaces
        sanitized_line=$(echo "$line" | sed 's/^\([^#]*=[^#]*\).*/\1/' | xargs)

        # Split the line into key and value based on the first '=' occurrence
        key="${sanitized_line%%=*}"
        value="${sanitized_line#*=}"

        # Trim spaces from key and value
        key=$(echo "$key" | xargs)
        value=$(echo "$value" | xargs)

        # Export the variable if it's non-empty
        if [[ -n "$value" ]]; then
            export "$key"="$value"
            echo_magenta "$key=$value"
        else
            echo_yellow "$key -> [SKIPPED]: value is empty"
        fi
    done
}

# Ensure the script is being called with the correct number of arguments
if [[ $# -gt 1 ]]; then
    echo "Usage: $0 <env_file>"
    exit 1
fi

echo_white "Setting environment variables..."
# Set environment variables from the file if provided, otherwise set defaults
if [[ -n "$1" ]]; then
    echo_white "  ... from file: $1"
    set_vars_from_file "$1"
else
    echo_yellow "  ... from defaults"
    set_default_vars
fi

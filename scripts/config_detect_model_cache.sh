#!/bin/bash

set -e  # Exit on error

# ####################################################################################################################
# Detects if the model cache docker override is required based on the (key=value) configuration file supplied.
# NOTE: If called from Makefile, requires the .env file to be generated first (via the 'config-generate-env' target).
# ####################################################################################################################

get_model_override_from_file() {
    ENV_VARS_FILE="$1"

    # Check if the file exists and is readable
    if [[ ! -f "$ENV_VARS_FILE" ]]; then
        echo ""  # Return empty value if the file does not exist
        return
    fi

    while IFS= read -r line; do
        # Remove inline comments and trim spaces
        sanitized_line=$(echo "$line" | sed 's/^\([^#]*=[^#]*\).*/\1/' | xargs)

        # Skip empty lines or commented lines
        [[ -z "$sanitized_line" || "$sanitized_line" =~ ^[[:space:]]*# ]] && continue

        # Split the line into key and value
        key="${sanitized_line%%=*}"
        value="${sanitized_line#*=}"

        # Trim spaces
        key=$(echo "$key" | xargs)
        value=$(echo "$value" | xargs)

        if [[ "$key" == "ENABLE_FIRST_TIME_CACHE" ]]; then
            # Strip surrounding quotes if present
            value=$(echo "$value" | sed -E 's/^"(.*)"$/\1/')

            # Check if value is set to 1, true, or yes (case insensitive)
            if [[ "$value" =~ ^(1|true|yes)$ ]]; then
                echo "-f docker-compose.model-cache.override.yaml"
            else
                echo ""
            fi
            return
        fi
    done < "$ENV_VARS_FILE"

    # Default to empty if key is not found
    echo ""
}

# Ensure the script is being called with at most one argument
if [[ $# -gt 1 ]]; then
    echo "Usage: $0 <env_file>"
    exit 1
fi

get_model_override_from_file "$1"

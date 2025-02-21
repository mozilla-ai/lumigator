#!/bin/bash

set -e  # Exit on error

# #######################
# Source common functions
# #######################
COMMON_FILE="$(dirname "$0")/common.sh"
if [ -f "$COMMON_FILE" ]; then
    source "$COMMON_FILE"
else
    echo "Error: common.sh not found!" >&2
    exit 1
fi

# #########################
# Merge configuration files
# #########################
merge_conf_files() {
    temp_file=$(mktemp)
    keys_order=()

    while IFS='=' read -r key value || [[ -n "$key" ]]; do
        [[ -z "$key" || "$key" =~ ^#.*$ ]] && continue
        # Remove existing key entry if found
        sed -i '' "/^$key=/d" "$temp_file" 2>/dev/null || sed -i "/^$key=/d" "$temp_file"
        # Append new value
        echo "$key=$value" >> "$temp_file"
        # Store key order if it's the first occurrence
        grep -q "^$key=" <<< "${keys_order[*]}" || keys_order+=("$key")
    done < <(cat "$@")

    # Print keys in original order with latest values
    for key in "${keys_order[@]}"; do
        grep "^$key=" "$temp_file"
    done

    rm "$temp_file"
}

# Main script logic for handling .env generation
generate_env() {
    CONFIG_BUILD_DIR="$1"
    CONFIG_DEFAULT_FILE="$2"
    CONFIG_OVERRIDE_FILE="$3"

    echo_white "Generating the .env file..."
    mkdir -p "$CONFIG_BUILD_DIR"  # Ensure the build (output) directory exists

    if [ -f "$CONFIG_OVERRIDE_FILE" ]; then
        echo_green "Found user configuration: '$CONFIG_OVERRIDE_FILE', overrides will be applied"
        merge_conf_files "$CONFIG_DEFAULT_FILE" "$CONFIG_OVERRIDE_FILE" > "$CONFIG_BUILD_DIR/.env"
    else
        echo_yellow "No user configuration found, default will be used: '$CONFIG_DEFAULT_FILE'"
        cp "$CONFIG_DEFAULT_FILE" "$CONFIG_BUILD_DIR/.env"
    fi

    echo_green "Config file generated: '$CONFIG_BUILD_DIR/.env'"
}

# Ensure the script is being called with the correct number of arguments
if [[ $# -lt 3 || $# -gt 4 ]]; then
    echo "Usage: $0 <config_build_dir> <config_user_dir> <config_file_default> [config_file_override]"
    exit 1
fi

# Call the function to generate the .env file
generate_env "$1" "$2" "$3" "$4"

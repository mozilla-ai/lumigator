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

# ###########################################################
# Track creation of temporary files in the script for cleanup
# ###########################################################
TEMP_FILES=()

# #######################################################
# Merge configuration files - last (key/value) write wins
# #######################################################
merge_conf_files() {
    temp_file=$(mktemp)
    TEMP_FILES+=("$temp_file")
    keys_order=()
    config_values=""

    # Process each file in order (later files/params override earlier ones)
    for file in "$@"; do
        [[ -f "$file" ]] || continue  # Skip missing files

        while IFS= read -r line || [[ -n "$line" ]]; do
            [[ -z "$line" || "$line" =~ ^#.*$ ]] && continue  # Skip empty/comment lines

            key="${line%%=*}"  # Extract key (before first '=')
            value="${line#*=}"  # Extract value (after first '=')

            # If key is new, add to the order list
            if ! grep -q "^$key=" <<< "$config_values"; then
                keys_order+=("$key")
            fi

            # Overwrite key-value pair
            config_values=$(printf "%s\n" "$config_values" | grep -v "^$key=")
            config_values+=$'\n'"$key=$value"
        done < "$file"
    done

    # Print merged key-value pairs in original order
    for key in "${keys_order[@]}"; do
        grep "^$key=" <<< "$config_values"
    done
}


# Main script logic for handling .env generation
generate_env() {
    CONFIG_BUILD_DIR="$1"
    CONFIG_USER_KEY_FILE="$2"
    CONFIG_USER_KEY_ENV_VAR="$3"
    CONFIG_DEFAULT_FILE="$4"
    CONFIG_OVERRIDE_FILE="$5"

    echo_white "Generating the .env file..."
    mkdir -p "$CONFIG_BUILD_DIR"  # Ensure the build (output) directory exists

    # Create a temp file to hold the env_var=value for the user's key.
    TEMP_USER_KEY_FILE=$(mktemp)
    TEMP_FILES+=("$TEMP_USER_KEY_FILE")

    # Check for the key file's existence and populate the temp file with KEY=VALUE so we can merge it
    if [ -f "$CONFIG_USER_KEY_FILE" ]; then
        USER_KEY_VALUE=$(tr -d '\n' < "$CONFIG_USER_KEY_FILE")  # Remove newlines
        echo "$CONFIG_USER_KEY_ENV_VAR=$USER_KEY_VALUE" > "$TEMP_USER_KEY_FILE"
    else
        echo_red "Error: Required user key file '$CONFIG_USER_KEY_FILE' not found. Exiting." >&2
        exit 1
    fi

    if [ -f "$CONFIG_OVERRIDE_FILE" ]; then
        echo_green "Found user configuration: '$CONFIG_OVERRIDE_FILE', overrides will be applied"
        merge_conf_files "$CONFIG_DEFAULT_FILE" "$CONFIG_OVERRIDE_FILE" "$TEMP_USER_KEY_FILE" > "$CONFIG_BUILD_DIR/.env"
    else
        echo_yellow "No user configuration found, default will be used for merge: '$CONFIG_DEFAULT_FILE'"
        merge_conf_files "$CONFIG_DEFAULT_FILE" "$TEMP_USER_KEY_FILE" > "$CONFIG_BUILD_DIR/.env"
    fi

    echo_green "Config file generated: '$CONFIG_BUILD_DIR/.env'"
}

# Ensure the script is being called with the correct number of arguments
if [[ $# -lt 4 || $# -gt 5 ]]; then
    echo "Usage: $0 <config_build_dir> <config_user_key_file> <config_user_key_env_var> <config_file_default> [config_file_override]"
    exit 1
fi

# Set up a global trap to clean up all temporary files when the script exits
trap 'rm -rf -- "${TEMP_FILES[@]}"' EXIT

# Call the function to generate the .env file
generate_env "$1" "$2" "$3" "$4" "$5"

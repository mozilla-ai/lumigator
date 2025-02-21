#!/bin/bash

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
# Ensure app encryption key
# #########################
generate_key() {
    APP_DIR="$1"
    KEY_FILE="$2"
    APP_ENV_VAR_NAME="$3"
    EXPECTED_APP_DIR_PERMS=700  # Secure permissions for dir (owner-only access)
    EXPECTED_KEY_PERMS=600 # Secure permissions for file (owner-only access)

    echo "Ensuring application encryption key (and directory) exists..."

    # Ensure we have a directory and not a file at the expected path if it already exists
    if [ -e "$APP_DIR" ] && [ ! -d "$APP_DIR" ]; then
        echo_red "Error: $APP_DIR exists but is not a directory!" >&2
        exit 1
    fi

    # Handle the case where we don't have a directory yet
    mkdir -p "$APP_DIR"

    # Check and update permissions if incorrect
    CURRENT_PERMS=$(stat -c "%a" "$APP_DIR" 2>/dev/null || stat -f "%A" "$APP_DIR")
    if [ "$CURRENT_PERMS" -ne "$EXPECTED_APP_DIR_PERMS" ]; then
        echo_yellow "Setting permissions for $APP_DIR (current: $CURRENT_PERMS, expected: $EXPECTED_APP_DIR_PERMS)"
        chmod "$EXPECTED_APP_DIR_PERMS" "$APP_DIR"
    fi

    # Check if key file exists with the right permissions, otherwise generate one for the user
    if [ ! -f "$KEY_FILE" ]; then
        echo_yellow "No key found. Generating a new AES-256 key..."
        openssl rand -base64 32 > "$KEY_FILE"
        chmod "$EXPECTED_KEY_PERMS" "$KEY_FILE"
        echo_green "Key generated and stored in $KEY_FILE"
    else
        echo_yellow "Existing key found in $KEY_FILE"
    fi

    # Check and fix permissions if incorrect
    CURRENT_KEY_PERMS=$(stat -c "%a" "$KEY_FILE" 2>/dev/null || stat -f "%A" "$KEY_FILE")
    if [ "$CURRENT_KEY_PERMS" -ne "$EXPECTED_KEY_PERMS" ]; then
        echo_yellow "Fixing permissions for $KEY_FILE (current: $CURRENT_KEY_PERMS, expected: $EXPECTED_KEY_PERMS)"
        chmod "$EXPECTED_KEY_PERMS" "$KEY_FILE"
    fi
}


# Ensure the script is being called with the correct number of arguments
if [[ $# -lt 3 || $# -gt 3 ]]; then
    echo "Usage: $0 <config_user_dir> <config_user_key_file> <config_user_key_env_var>"
    exit 1
fi

# Call the function to generate the key
generate_key "$1" "$2" "$3"

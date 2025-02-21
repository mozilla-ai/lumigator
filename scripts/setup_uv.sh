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

# ##########
# Install UV
# ##########

# Expected installation path for uv
# See: https://docs.astral.sh/uv/configuration/installer/#changing-the-install-path
LOCAL_BIN="$HOME/.local/bin"

# Ensure the directory exists
mkdir -p "$LOCAL_BIN"

# Check if LOCAL_BIN is in PATH
PATH_PRESENT=0
for p in $(echo "$PATH" | tr ':' '\n'); do
    if [ "$p" = "$LOCAL_BIN" ]; then
        PATH_PRESENT=1
        break
    fi
done

# If not in PATH, add it temporarily and suggest making it permanent
if [ "$PATH_PRESENT" -eq 0 ]; then
    echo_red "PATH does not contain '$LOCAL_BIN' (installation directory). Adding temporarily..."
    export PATH="$LOCAL_BIN:$PATH"
fi

# Install uv if not found
UV_INSTALL_REQUIRED=0
if ! command -v uv >/dev/null 2>&1; then
    echo_red "uv not found. Installing..."
    curl -LsSf https://astral.sh/uv/install.sh | env UV_INSTALL_DIR="$LOCAL_BIN" sh
    UV_INSTALL_REQUIRED=1
fi

# ######################################
# Configure Virtual Environments for UV
# ######################################

# Store the original directory
original_dir=$(pwd)

# Get all the sub-projects with a pyproject.toml under lumigator/ (ignoring existing .venvs)
dirs=()
while IFS= read -r file; do
    dir=$(dirname "$file")
    dir=${dir#./}  # Remove leading "./"
    dirs+=("$dir")
done < <(find ./lumigator -name "pyproject.toml" -not -path "*/.venv/*")

# Track .venv locations
venv_locations=()

# Create a .venv and sync deps for each project
for project in "${dirs[@]}"; do
    venv_dir="$project/.venv"
    # Create virtual environment
    uv venv "$venv_dir"
    # Add the venv directory to the tracking array
    venv_locations+=("$venv_dir")
    # Sync the new .venv
    cd "$project" && uv sync || exit && uv sync --dev || exit
    # Return back to the root directory so the next iteration can use the relative path
    cd "$original_dir" || exit
done

# Sync root deps
uv sync && uv sync --dev

if [ "$PATH_PRESENT" -eq 0 ]; then
    echo_yellow "The PATH was temporaily updated to include '$LOCAL_BIN'"
    echo_yellow "To make this change permanent, add the following line to your shell profile:"
    echo ""
    echo_white "    export PATH=\"$LOCAL_BIN:\$PATH\""
    echo ""
    echo_yellow "Depending on your installation directory, you may be able to use generic shell environment variables:"
    echo ""
    echo_white "    export PATH=\"\$HOME/.local/bin:\$PATH\""
    echo ""
fi

if [ "$UV_INSTALL_REQUIRED" -eq 1 ]; then
    echo_green "Package manager 'uv' has been installed at '$LOCAL_BIN'."
fi

echo_green "Virtual environments created at the following locations:"
for venv in "${venv_locations[@]}"; do
    echo_white "    $venv"
done

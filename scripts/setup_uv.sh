#!/usr/bin/env bash

set -e  # Exit on error

#!/bin/bash

# ###############
# Colorful output
# ###############

red() {
    echo -e "\033[1;31m$1\033[0m"
}

yellow() {
    echo -e "\033[1;33m$1\033[0m"
}

green() {
    echo -e "\033[1;32m$1\033[0m"
}

white() {
    echo -e "\033[1;37m$1\033[0m"
}

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
    red "PATH does not contain '$LOCAL_BIN' (installation directory). Adding temporarily..."
    export PATH="$LOCAL_BIN:$PATH"
    echo -e "\033[1;33mTo use uv from the command line, add the following line to your profile:\033[0m"
    echo ""
    echo "    export PATH=\"$LOCAL_BIN:\$PATH\""
    echo ""
    yellow "Depending on your installation directory, you may be able to use generic shell environment variables:"
    echo ""
    white "    export PATH=\"\$HOME/.local/bin:\$PATH\""
    echo ""
fi

# Install uv if not found
if ! command -v uv >/dev/null 2>&1; then
    red "uv not found. Installing..."
    curl -LsSf https://astral.sh/uv/install.sh | env UV_INSTALL_DIR="$LOCAL_BIN" sh
fi

# Now, run the setup for virtual environments
export PATH="$LOCAL_BIN:$PATH"

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

green "Package manager 'uv' has been installed at '$LOCAL_BIN'."
yellow "You may need to add this location to your PATH in your profile."

green "Virtual environments created at the following locations:"
for venv in "${venv_locations[@]}"; do
    white "    $venv"
done

#!/bin/bash

# Store the original directory
original_dir=$(pwd)

# Get all the sub-projects with a pyproject.toml under lumigator/
dirs=()
while IFS= read -r file; do
    dir=$(dirname "$file")
    dir=${dir#./}  # Remove leading "./"
    dirs+=("$dir")
done < <(find ./lumigator -name "pyproject.toml" -not -path "*/.venv/*")

# Create a .venv and sync deps for each project
for project in "${dirs[@]}"; do
    uv venv "$project/.venv" --relocatable
    cd "$project" && uv sync || exit && uv sync --dev || exit
    # Return back to the root directory so the next iteration can use the relative path
    cd "$original_dir" || exit
done

# Sync root deps
uv sync && uv sync --dev

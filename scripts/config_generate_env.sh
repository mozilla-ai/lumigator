#!/bin/bash

merge_env_files() {
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

if [[ $# -lt 1 || $# -gt 2 ]]; then
    echo "Usage: $0 <env_file1> [env_file2]"
    exit 1
fi

merge_env_files "$@"

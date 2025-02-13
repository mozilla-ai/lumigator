#!/bin/bash

# Given an input YAML file and a destination file this will attempt
# to parse and flatten YAML into a .env compatible format.
yq eval '
  .app // {}
  | to_entries
  | map(.key |= upcase)
  | map(
    with(select(.value | kind == "seq");
        .value = (.value | join(","))
    ) |
    with(select(.value | kind == "scalar");
        .value = .value
    )
  )
  | map(.value |= to_string)
  | map("\(.key)=\(.value)")
  | .[] ' - "$1" > "$2";

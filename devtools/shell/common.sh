#!/usr/bin/env bash
set -eou pipefail

# Requires curl.


function check_if_installed() {
	tool=$1
	test=$(command -v "$tool")
	# return a 0 if this is not found; command output is nil if the tool isn't there
	if [[ -z $test ]]; then
		echo "0"
	else
		echo "$test"
	fi
}

PLAT=$(uname -o)
CUDA_AVAILABLE=$(check_if_installed nvcc)
TORCH_VERSION="2.4.0"
TORCH_CUDA_VERSION="cu121"
LUMIGATOR_PATH="${HOME}/workspace/lumigator"

export PLAT
export CUDA_AVAILABLE
export TORCH_VERSION
export TORCH_CUDA_VERSION
export LUMIGATOR_PATH

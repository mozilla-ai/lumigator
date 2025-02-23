#!/bin/bash

set -e  # Exit on error

# Prevent duplicate loading
if [ -n "$COMMON_SH_LOADED" ]; then
    return
fi
COMMON_SH_LOADED=1

# ########################
# Colorful terminal output
# ########################
echo_red() {
    echo -e "\033[1;31m$1\033[0m"
}

echo_yellow() {
    echo -e "\033[1;33m$1\033[0m"
}

echo_green() {
    echo -e "\033[1;32m$1\033[0m"
}

echo_white() {
    echo -e "\033[1;37m$1\033[0m"
}

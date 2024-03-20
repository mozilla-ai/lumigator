#!/usr/bin/env bash

set -e
set -x

ruff src
ruff format src --check

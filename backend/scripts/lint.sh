#!/usr/bin/env bash

set -e
set -x

ruff check src
ruff format src --check

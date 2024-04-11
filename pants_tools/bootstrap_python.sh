#!/usr/bin/env bash
set -eou pipefail

RELEASE=$(curl https://raw.githubusercontent.com/indygreg/python-build-standalone/latest-release/latest-release.json)
URL=$(echo "$RELEASE" | jq ".asset_url_prefix" -r)
TAG=$(echo "$RELEASE" | jq ".tag" -r)
PY_VERSION="3.10.13"
DEBIAN="cpython-${PY_VERSION}+${TAG}-x86_64-unknown-linux-gnu-pgo+lto-full.tar.zst"
DARWIN="cpython-${PY_VERSION}+${TAG}-aarch64-apple-darwin-pgo+lto-full.tar.zst"

LOCAL_PYTHON_PATH="$HOME/workspace/.pythoninterpreters/python${PY_VERSION}"
mkdir -p "$LOCAL_PYTHON_PATH"
cd "$LOCAL_PYTHON_PATH"
(set +o pipefail ; rm -r *python*)

arch=${1:-Darwin}
if [[ $arch == "Darwin" ]]; then
  wget "$URL/$DARWIN"
  tarbase=${DARWIN%.*}
  zstd -d "$DARWIN"
  tar xzf "${tarbase}"
elif [[ $arch  == "debian" ]]; then
  wget "$URL/$DEBIAN"
  tar -axvf "$DEBIAN"
else
  echo "no platform passed"
fi

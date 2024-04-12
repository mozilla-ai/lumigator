#!/usr/bin/env bash
set -eou pipefail

RELEASE=$(curl https://raw.githubusercontent.com/indygreg/python-build-standalone/latest-release/latest-release.json)
URL=$(echo "$RELEASE" | jq ".asset_url_prefix" -r)
TAG=$(echo "$RELEASE" | jq ".tag" -r)
PY_VERSION="3.10.13"
DEBIAN="cpython-${PY_VERSION}+${TAG}-x86_64-unknown-linux-gnu-pgo+lto-full.tar.zst"
DARWIN="cpython-${PY_VERSION}+${TAG}-aarch64-apple-darwin-pgo+lto-full.tar.zst"

LOCAL_PYTHON_PATH="$HOME/workspace/.pythoninterpreters/python${PY_VERSION}"
INTERPRETER="${LOCAL_PYTHON_PATH}/python/install/bin/python3"
mkdir -p "$LOCAL_PYTHON_PATH"
pushd "$LOCAL_PYTHON_PATH"
echo "cleaning previous installation at $LOCAL_PYTHON_PATH"
rm -r ./*python* || true

arch=${1:-Darwin}
if [[ $arch == "Darwin" ]]; then
  echo "installing macos interpreter"
  wget "$URL/$DARWIN"
  tarbase=${DARWIN%.*}
  zstd -d "$DARWIN"
  tar xzf "${tarbase}"
  rm cpython*
  cd "$WORKSPACE/mzai-platform/"

  echo "updating local platform tags file"
  macos_tags_file="$WORKSPACE/mzai-platform/pants_tools/macosx_14_pex_platform_tags.json"
	cat "$macos_tags_file" | jq '.path = "'"$INTERPRETER"'"' > "${macos_tags_file}.new"
	mv "${macos_tags_file}.new" "$macos_tags_file"

	printf "interpreter is available at\n%s\n and is not on your PATH. use it explicitly if you'd like" "$INTERPRETER"



elif [[ $arch  == "debian" ]]; then
  echo "installing debian interpreter"
  wget "$URL/$DEBIAN"
  tar -axvf "$DEBIAN"
else
  echo "no platform passed"
fi

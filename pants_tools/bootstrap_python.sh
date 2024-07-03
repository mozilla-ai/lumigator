#!/usr/bin/env bash
set -eou pipefail
PY_VERSION=${MZAI_PY_VERISON:-3.11.9}
# this is the release tag - see https://github.com/indygreg/python-build-standalone/releases/
TAG="20240415"
URL="https://github.com/indygreg/python-build-standalone/releases/download/$TAG"
DEBIAN="cpython-${PY_VERSION}+${TAG}-x86_64-unknown-linux-gnu-pgo+lto-full.tar.zst"
DARWIN="cpython-${PY_VERSION}+${TAG}-aarch64-apple-darwin-pgo+lto-full.tar.zst"
REPOROOT=$(git rev-parse --show-toplevel)
LOCAL_PYTHON_PATH="$REPOROOT/.python/python${PY_VERSION}"
INTERPRETER="${LOCAL_PYTHON_PATH}/python/install/bin/python3"
mkdir -p "$LOCAL_PYTHON_PATH"
pushd "$LOCAL_PYTHON_PATH"
echo "cleaning previous installation at $LOCAL_PYTHON_PATH"
rm -r ./*python* || true  # hack for make to have this  always return true.

arch=${1:-Darwin}
if [[ $arch == "Darwin" ]]; then
  echo "installing macos interpreter from $URL/$DARWIN"
  wget -nv "$URL/$DARWIN"
  tarbase=${DARWIN%.*}
  zstd -d "$DARWIN"
  tar xzf "${tarbase}"
  rm cpython*
  cd "$REPOROOT"

#  echo "updating local platform tags file"
#  macos_tags_file="$REPOROOT/pants_tools/python_3_11_9_macosx_14_pex_platform_tags.json"
#	cat "$macos_tags_file" | jq '.path = "'"$INTERPRETER"'"' > "${macos_tags_file}.new"
#	mv "${macos_tags_file}.new" "$macos_tags_file"
	printf "interpreter is available at\n%s\n and is not on your PATH. use it explicitly if you'd like" "$INTERPRETER"


elif [[ $arch  == "GNU/Linux" ]]; then
  echo "installing debian interpreter"
  wget -nv "$URL/$DEBIAN"
  tar -axf "$DEBIAN"
  rm cpython* || true
	printf "interpreter is available at\n%s\n and is not on your PATH. use it explicitly if you'd like" "$INTERPRETER"
else
  echo "$arch was passed but isn't valid. exiting!"
fi

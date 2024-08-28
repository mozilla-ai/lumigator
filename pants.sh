#!/usr/bin/env bash
# this script is to help ease using parametrization in Pants.
# most targets will take a parametrize argument and this will ensure
# that a command is used with a _single_ parametrization, not multiple.

plat=$(uname -o)
PLAT=${plat,,}  # lowercase

if [[ "$PLAT" == "darwin" ]]; then
 PARAMETRIZE="darwin"
else
  if [[ $(command -v nvcc >/dev/null 2>&1) ]]; then
    echo "Running on Linux and found nvcc; setting env var to use the linux_cuda python lockfile."
    echo "if you cannot use cuda in pytorch/etc., there might be an issue with how pants sees the resolves."
    PARAMETRIZE="linux_cuda"
  else
    PARAMETRIZE="linux_cpu"
  fi
fi

if [[ "$#" == 0 ]]; then
  echo "no goal or target"
else
  echo "~~~~ pants platform parametrizer ~~~~"
  echo "running the following pants command:"
  echo "$(which pants)" "${*}@parametrize=${PARAMETRIZE}"
  echo "~~~~~~~~"
  echo ""
  $(which pants) ${*}@parametrize=${PARAMETRIZE}
  # shellcheck disable=SC2181
  if [[ "$?" != 0 ]]; then
    echo "~~~~ pants platform parametrizer ~~~~"
    echo "it's possible you don't need to use this script - run your pants command again without it like:"
    echo ""
    echo pants "${*}"
    echo "~~~~~~~"
  fi
fi

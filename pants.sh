#!/usr/bin/env bash
# this script is to help ease using parametrization in Pants.
# most targets will take a parametrize argument and this will ensure
# that a command is used with a _single_ parametrization, not multiple.

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


CUDA_AVAILABLE=$(check_if_installed nvcc)
PLAT=$(uname -o)

if [[ "$PLAT" == "Darwin" ]]; then
 PARAMETRIZE="darwin"
else
  if [[ "$CUDA_AVAILABLE" != 0  ]]; then
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

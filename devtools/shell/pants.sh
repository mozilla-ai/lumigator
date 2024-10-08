#!/usr/bin/env bash
set -eou pipefail
# this script is to help ease using parametrization in Pants.
# most targets will take a parametrize argument and this will ensure
# that a command is used with a _single_ parametrization, not multiple.

if [[ -f "devtools/shell/common.sh" ]]; then
	source devtools/shell/common.sh
elif [[ -f "common.sh" ]]; then
	source common.sh
else
	echo "cannot find common.sh; exiting"
	exit 1
fi

# sourced from common
CUDA_AVAILABLE=$(check_if_installed nvcc)
PLAT=$(uname -o)

if [[ "$PLAT" == "Darwin" ]]; then
	PARAMETRIZE="darwin"
else
	if [[ "$CUDA_AVAILABLE" != 0 ]]; then
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
	pushd "${LUMIGATOR_PATH}"
	echo "~~~~ pants platform parametrizer ~~~~"
	echo "running the following pants command:"
	echo "$(which pants)" "${*}@parametrize=${PARAMETRIZE}"
	echo "~~~~~~~~"
	echo ""
	pants_finished_file=".pants_complete.lock"
	touch ${pants_finished_file}
	$(which pants) ${*}@parametrize=${PARAMETRIZE} && rm ${pants_finished_file}
	if [[ -f ${pants_finished_file} ]]; then
		rm ${pants_finished_file}
		echo "~~~~ pants platform parametrizer ~~~~"
		echo "previous invocation failed - running your pants command again without it like:"
		echo ""
		echo pants "${*}"
		echo "~~~~~~~"
		$(which pants) ${*}
	fi
	popd
fi

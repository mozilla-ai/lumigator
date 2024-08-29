#!/usr/bin/env bash
set -eou pipefail

# Requires curl.

function check_if_installed() {
	tool=$1
	test=$(command -v "$tool")
	if [[ -z $test ]]; then
		echo "0"
	else
		echo "$test"
	fi
}

plat=$(uname -o)
PLAT=${plat}
PY_VERSION=${MZAI_PY_VERISON:-3.11.9}
PYTHON_INSTALLED=$(check_if_installed python)
CUDA_AVAILABLE=$(check_if_installed nvcc)
TORCH_VERSION="2.4.0"
TORCH_CUDA_VERSION="cu121"
UV_INSTALLED=$(check_if_installed uv)
VENVNAME="mzaivenv"

if [[ $PLAT == 'GNU/Linux' ]]; then
	echo "linux platform detected"
	UV_ARGS=("--index-strategy=unsafe-best-match" "--override" "tmp_overrides.txt")
	if [[ "$CUDA_AVAILABLE" != 0 ]]; then
		echo "nvcc found; configuring with CUDA"
		PYTHON_INSTALL_DIR=/opt/python
		PY_NAME=cpython-3.11.9-linux-x86_64-gnu
		PYTHON=${PYTHON_INSTALL_DIR}/${PY_NAME}/bin/python3
		echo "torch[cuda]==${TORCH_VERSION}+${TORCH_CUDA_VERSION}" >tmp_overrides.txt
		UV_ARGS+=("--extra-index-url" "https://download.pytorch.org/whl/${TORCH_CUDA_VERSION}")
	else
		PYTHON_INSTALL_DIR=/opt/python
		PY_NAME=cpython-3.11.9-linux-x86_64-gnu
		PYTHON=${PYTHON_INSTALL_DIR}/${PY_NAME}/bin/python3
		echo "torch==2.4.0+cpu" >tmp_overrides.txt
		UV_ARGS+=("--extra-index-url" "https://download.pytorch.org/whl/cpu")
	fi
else
	echo "Darwin setup"
	PYTHON_INSTALL_DIR=.python
	PY_NAME=cpython-3.11.9-macos-aarch64-none
	PYTHON=${PYTHON_INSTALL_DIR}/${PY_NAME}/bin/python3
	echo "torch==2.4.0" >tmp_overrides.txt
	UV_ARGS=("--index-strategy=unsafe-best-match")
fi

function install_uv() {
	if [[ "$UV_INSTALLED" == 0 ]]; then
		echo "installing UV from source"
		curl -LsSf https://astral.sh/uv/install.sh | sh
		UV_BIN="$HOME/.cargo/bin/uv"
	else
		echo "UV is available at $UV_INSTALLED"
		UV_BIN=${UV_INSTALLED}
	fi
	export UV_BIN
}

function install_python() {
	if [[ "$PYTHON_INSTALLED" != 0 ]]; then
		if [[ $("$PYTHON_INSTALLED" --version) == "Python ${PY_VERSION}" ]]; then
			echo "Local compatible python found at $PYTHON_INSTALLED"
			PYTHON="$PYTHON_INSTALLED"
		else
			echo "Local python found at $PYTHON_INSTALLED is not the right version - installing from UV"
			"$UV_BIN" python install "$PY_VERSION" --python-preference only-managed
		fi
	else
		echo "installing python interpreter from UV"
		"$UV_BIN" python install "$PY_VERSION" --python-preference only-managed
	fi
}

function install_venv() {
	if [[ ! -e "$VENVNAME" ]]; then
		echo "making a virtual env and installing the suite of deps into it."
		"$UV_BIN" venv "$VENVNAME" --seed --python "$PYTHON"
		# shellcheck source=/dev/null
		source "$VENVNAME/bin/activate"
		pip_cmd=("$UV_BIN" "pip" "install" "-r" "3rdparty/python/pyproject.toml" "${UV_ARGS[@]}")
		echo "running the following:"
		echo "${pip_cmd[@]}"
		"${pip_cmd[@]}"
		rm tmp_overrides.txt || true
	else
		echo "found a directory where the venv is supposed to be - remove it if you want to install there."
	fi
	echo "Activate the venv with the following command:"
	echo ""
	echo "source $VENVNAME/bin/activate"
}

UV_PYTHON_INSTALL_DIR=$PYTHON_INSTALL_DIR
export UV_PYTHON_INSTALL_DIR
install_uv
install_python
install_venv

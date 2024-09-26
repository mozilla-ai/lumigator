# TODO
# * set token from env var
# * set directory to host mounted dir
# * copy lumigator demo to host mmounted dir
mkdir -p /etc/lumigator/data/jupyter/
cp -R /mzai/notebooks /etc/lumigator/data/jupyter/
pushd  /etc/lumigator/data/jupyter/notebooks
LUMIGATOR_SERVICE_HOST="localhost" RAYCLUSTER_KUBERAY_HEAD_SVC_PORT_8265_TCP_ADDR="localhost" JUPYTERLAB_SETTINGS_DIR=/etc/lumigator/data/jupyter/ /usr/local/bin/jupyter-lab --ip "0.0.0.0" &
echo $! > /etc/lumigator/data/jupyter/jupyter.pid
popd
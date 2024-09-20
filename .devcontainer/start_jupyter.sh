LUMIGATOR_SERVICE_HOST="localhost" RAYCLUSTER_KUBERAY_HEAD_SVC_PORT_8265_TCP_ADDR="localhost" /usr/local/bin/jupyter-lab &
mkdir -p /etc/lumigator/data/jupyter/
echo $! > /etc/lumigator/data/jupyter/jupyter.pid
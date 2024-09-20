# prepare minio
mkdir -p /etc/minio/data

# MINIO_ROOT_USER=""
# MINIO_ROOT_PASSWORD=""

# start minio
minio server /etc/minio/data/ --console-address ":12345" &

# configure postgres
export POSTGRES_USER=admin
export POSTGRES_PASSWORD=password
export POSTGRES_DB=lumigator
# ...

ray start --head --port=6379
# systemctl start minio.service

LUMIGATOR_SERVICE_HOST="localhost" RAYCLUSTER_KUBERAY_HEAD_SVC_PORT_8265_TCP_ADDR="localhost" /Users/jtramon/work/lumigator/mzaivenv/bin/jupyter-lab
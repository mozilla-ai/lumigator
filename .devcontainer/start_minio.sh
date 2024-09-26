mkdir -p /etc/lumigator/data/s3
cd /etc/lumigator/data/s3
cp /mzai/.devcontainer/minio_policy.json /etc/lumigator/data/s3
minio server start &
echo $! > /etc/lumigator/data/s3/minio.pid
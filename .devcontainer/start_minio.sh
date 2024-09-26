mkdir -p /etc/lumigator/data/s3
cd /etc/lumigator/data/s3
minio server start &
export PATH=$PATH:/etc/lumigator/minio
export MC_CONFIG_DIR=/etc/lumigator/minio/config
until mc alias set lumigator_s3 http://127.0.0.1:9000 minioadmin minioadmin; do echo "Waiting for minio"; sleep 3; done
mc admin user add lumigator_s3 lumigator lumigator
mc admin policy attach lumigator_s3 readwrite --user lumigator
echo $! > /etc/lumigator/data/s3/minio.pid
groupadd minio
useradd -s /bin/bash -m -g minio minio
mkdir /tmp/minio-install
pushd /tmp/minio-install
mkdir -p /etc/lumigator/minio
mkdir -p /etc/lumigator/minio/config 
wget https://dl.min.io/server/minio/release/linux-arm64/archive/minio_20240913202602.0.0_arm64.deb -O minio.deb
curl https://dl.min.io/client/mc/release/linux-arm64/mc \
  --create-dirs \
  -o /etc/lumigator/minio/mc
chmod +x /etc/lumigator/minio/mc
export PATH=$PATH:/etc/lumigator/minio
export MC_CONFIG_DIR=/etc/lumigator/minio/config
mc alias set lumigator_s3 http://127.0.0.1:9000 minioadmin minioadmin
mc admin user add lumigator_s3 lumigator lumigator
mc admin policy attach lumigator readwrite --user lumigator_s3
dpkg -i minio.deb
popd
rm -rf /tmp/minio-install
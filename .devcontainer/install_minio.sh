groupadd minio
useradd -s /bin/bash -m -g minio minio
mkdir /tmp/minio-install
pushd /tmp/minio-install
mkdir -p /etc/lumigator/minio
mkdir -p /etc/lumigator/minio/config
chown -R minio /etc/lumigator/minio/config
wget https://dl.min.io/server/minio/release/linux-arm64/archive/minio_20240913202602.0.0_arm64.deb -O minio.deb
dpkg -i minio.deb
curl https://dl.min.io/client/mc/release/linux-arm64/mc \
  --create-dirs \
  -o /etc/lumigator/minio/mc
chmod +x /etc/lumigator/minio/mc
popd
rm -rf /tmp/minio-install
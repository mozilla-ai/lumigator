groupadd minio
useradd -s /bin/bash -m -g minio minio
mkdir /tmp/minio-install
pushd /tmp/minio-install
wget https://dl.min.io/server/minio/release/linux-arm64/archive/minio_20240913202602.0.0_arm64.deb -O minio.deb
dpkg -i minio.deb
popd
rm -rf /tmp/minio-install
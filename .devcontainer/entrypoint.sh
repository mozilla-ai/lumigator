su -c /etc/lumigator/startup/start_postgres.sh postgres
su -c /etc/lumigator/startup/start_minio.sh minio
su -c /etc/lumigator/startup/start_ray.sh ray
su -c /etc/lumigator/startup/start_jupyter.sh jupyter
cd /mzai
PYTHONPATH=/mzai:/mzai/lumigator/python/mzai:/mzai/lumigator/python uvicorn backend.main:app --host "0.0.0.0" --port 80 --reload


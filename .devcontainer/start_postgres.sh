mkdir -p /etc/lumigator/data/db/
cd /etc/lumigator/data/db

su -c "psql -c \"CREATE USER ${POSTGRES_USER} WITH PASSWORD '${POSTGRES_PASSWORD}';\"" postgres
su -c "psql -c \"CREATE DATABASE ${POSTGRES_DB} OWNER ${POSTGRES_USER}\"" postgres
su -c "psql -c \"GRANT ALL ON SCHEMA public TO ${POSTGRES_USER};\"" postgres
/usr/lib/postgresql/15/bin/postgres -D /etc/postgresql/15/main/ &
echo $! > /etc/lumigator/data/db/postgres.pid
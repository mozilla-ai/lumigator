mkdir -p /etc/lumigator/data/db/
cd /etc/lumigator/data/db

/usr/lib/postgresql/15/bin/postgres -D /etc/postgresql/15/main/ &
echo $! > /etc/lumigator/data/db/postgres.pid

until psql -c "SELECT current_timestamp - pg_postmaster_start_time();"; do echo "Waiting for postgres"; sleep 3; done

psql -c "CREATE USER ${POSTGRES_USER} WITH PASSWORD '${POSTGRES_PASSWORD}';"
psql -c "CREATE DATABASE ${POSTGRES_DB} OWNER ${POSTGRES_USER}"
psql -c "GRANT ALL ON SCHEMA public TO ${POSTGRES_USER};"

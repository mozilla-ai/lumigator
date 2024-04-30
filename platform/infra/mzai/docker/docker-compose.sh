#!/usr/bin/env bash

ROOT="infra/mzai/docker"
COMPOSE_FILE="$ROOT/docker-compose.yaml"
ENV_FILE="$ROOT/.env.local"

config() {
	docker compose -f ${COMPOSE_FILE} --env-file ${ENV_FILE} config
}

down() {
	docker compose -f ${COMPOSE_FILE} --env-file ${ENV_FILE} down
}

up() {
	down
	docker compose -f ${COMPOSE_FILE} --env-file ${ENV_FILE} up -d
}

case "$1" in
build)
	docker compose -f ${COMPOSE_FILE} --env-file ${ENV_FILE} build
	;;

up)
	up
	;;

down)
	down
	;;

config)
	config
	;;

*)
	echo "bad arg"
	;;
esac

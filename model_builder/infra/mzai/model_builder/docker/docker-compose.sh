#!/usr/bin/env bash

ROOT="infra/mzai/model_builder/docker"
COMPOSE_FILE="$ROOT/docker-compose.yaml"
ENV_FILE="$ROOT/.env.local"

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

*)
	echo "bad arg"
	;;
esac

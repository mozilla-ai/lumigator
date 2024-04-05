#!/usr/bin/env bash

COMPOSE_FILE=docker-compose.yaml
ENV_FILE=.env.local

down() {
	docker compose -f ${COMPOSE_FILE} --env-file ${ENV_FILE} down
}

up() {
	down
	docker compose -f ${COMPOSE_FILE} --env-file ${ENV_FILE} up -d
}

case "$1" in
build)
	echo "Downloading $2..."
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

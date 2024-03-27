DOCKER_DIR=infra/docker
COMPOSE_FILE=${DOCKER_DIR}/docker-compose.yaml
ENV_FILE=${DOCKER_DIR}/.env.local

build:
	docker compose -f ${COMPOSE_FILE} --env-file ${ENV_FILE} build

config:
	docker compose -f ${COMPOSE_FILE} --env-file ${ENV_FILE} config

up:
	docker compose -f ${COMPOSE_FILE} --env-file ${ENV_FILE} up -d

down:
	docker compose -f ${COMPOSE_FILE} --env-file ${ENV_FILE} down

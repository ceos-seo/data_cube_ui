SHELL:=/bin/bash
# Set the project name to the path - making underscore the path separator.
# Remove the leading slash and use lowercase since docker-compose will.
project_name=$(shell PWD_var=$$(pwd); PWD_no_lead_slash=$${PWD_var:1}; echo $${PWD_no_lead_slash//\//_} | awk '{print tolower($$0)}' | cat)
docker_compose_dev = docker-compose --project-directory build/docker/dev -f build/docker/dev/docker-compose.yml -p $(project_name)

# The `export` here is to allow commands (notably `docker-compose`) 
# in the Make targets to use them. 
IMG_REPO?=jcrattzama/data_cube_ui
IMG_VER?=
ODC_VER?=1.8.3

WORKDIR=/app

BASE_IMG_1_8_3='jcrattzama/datacube-base:odc1.8.3'
ifeq (${ODC_VER}, 1.8.3)
	BASE_IMG=${BASE_IMG_1_8_3}
	UI_BASE_IMG="${IMG_REPO}:odc${ODC_VER}${IMG_VER}_base"
endif

PROD_OUT_IMG?="${IMG_REPO}:odc${ODC_VER}${IMG_VER}"
DEV_OUT_IMG?="${IMG_REPO}:odc${ODC_VER}${IMG_VER}_dev"

COMMON_EXPRTS=export WORKDIR=${WORKDIR}
BASE_COMMON_EXPRTS=export OUT_IMG=${UI_BASE_IMG}; export BASE_IMG=${BASE_IMG}; ${COMMON_EXPRTS}
PROD_COMMON_EXPRTS=export OUT_IMG=${PROD_OUT_IMG}; export BASE_IMG=${UI_BASE_IMG}; ${COMMON_EXPRTS}
DEV_COMMON_EXPRTS=export OUT_IMG=${DEV_OUT_IMG};  export BASE_IMG=${UI_BASE_IMG}; ${COMMON_EXPRTS}

## Base ##
base-build:
	docker build . -f build/docker/base/Dockerfile --build-arg BASE_IMG=${BASE_IMG} -t ${UI_BASE_IMG}

base-run:
	docker run -it ${UI_BASE_IMG} bash

base-pull:
	docker pull ${UI_BASE_IMG}

base-push:
	docker push ${UI_BASE_IMG}
## End Base ##

## Development ##

# `rcv`: recursive.
dev-build-no-rcv:
	(${DEV_COMMON_EXPRTS}; $(docker_compose_dev) build)

dev-build: base-build dev-build-no-rcv

# Start the UI
dev-up: base-build
	(${DEV_COMMON_EXPRTS}; $(docker_compose_dev) up -d --build)

# Start without rebuilding the Docker image
# (use when dependencies have not changed for faster starts).
dev-up-no-build: 
	(${DEV_COMMON_EXPRTS}; $(docker_compose_dev) up -d)

# Stop the UI
dev-down:
	(${DEV_COMMON_EXPRTS}; $(docker_compose_dev) down --remove-orphans)

dev-restart: dev-down dev-up

dev-restart-no-build: dev-down dev-up-no-build

# List the running containers.
dev-ps:
	$(docker_compose_dev) ps

# Connect to the running UI container.
dev-ssh:
	$(docker_compose_dev) exec ui bash

# Delete everything
dev-clear:
	$(docker_compose_dev) stop
	$(docker_compose_dev) rm -fs

dev-pull-no-rcv:
	docker pull ${DEV_OUT_IMG}

dev-pull: base-pull dev-pull-no-rcv

dev-push:
	docker push ${DEV_OUT_IMG}
## End Development ##

## ODC Docker Network ##
# Create the `odc` network on which everything runs.
create-odc-network:
	docker network create odc

delete-odc-network:
	docker network rm odc
## End ODC Docker Network ##

## ODC DB ##
# Create the persistent volume for the ODC database.
create-odc-db-volume:
	docker volume create odc-db-vol

# Delete the persistent volume for the ODC database.
delete-odc-db-volume:
	docker volume rm odc-db-vol

recreate-odc-db-volume: delete-odc-db-volume create-odc-db-volume

# Create the ODC database Docker container.
# The `-N` argument sets the maximum number of concurrent connections (`max_connections`).
# The `-B` argument sets the shared buffer size (`shared_buffers`).
create-odc-db:
	docker run -d \
	-e POSTGRES_DB=datacube \
	-e POSTGRES_USER=dc_user \
	-e POSTGRES_PASSWORD=localuser1234 \
	--name=odc-db \
	--network="odc" \
	-v odc-db-vol:/var/lib/postgresql/data \
	postgis/postgis:10-2.5 \
	-N 1000 \
	-B 2048MB
	# postgres:10-alpine

start-odc-db:
	docker start odc-db

stop-odc-db:
	docker stop odc-db

odc-db-ssh:
	docker exec -it odc-db bash

dev-odc-db-init:
	$(docker_compose_dev) exec ui datacube system init

restart-odc-db: stop-odc-db start-odc-db

delete-odc-db:
	docker rm odc-db

recreate-odc-db: stop-odc-db delete-odc-db create-odc-db

recreate-odc-db-and-vol: stop-odc-db delete-odc-db recreate-odc-db-volume create-odc-db
## End ODC DB ##

## Django DB ##
# Create the persistent volume for the Django database.
dev-create-django-db-volume:
	docker volume create django-db-vol

# Delete the persistent volume for the Django database.
dev-delete-django-db-volume:
	docker volume rm django-db-vol

recreate-django-db-volume: dev-down dev-delete-django-db-volume dev-create-django-db-volume
## End Django DB ##

## Docker Misc ##
sudo-ubuntu-install-docker:
	sudo apt-get update
	sudo apt install -y docker.io
	sudo curl -L "https://github.com/docker/compose/releases/download/1.27.4/docker-compose-Linux-x86_64" -o /usr/local/bin/docker-compose
	sudo chmod +x /usr/local/bin/docker-compose
	sudo systemctl start docker
	sudo systemctl enable docker
	# The following steps are for enabling use 
	# of the `docker` command for the current user
	# without using `sudo`
	getent group docker || sudo groupadd docker
	sudo usermod -aG docker ${USER}
## End Docker Misc ##

## Native Install ##

# TODO: native-build:

## End Native Install ##
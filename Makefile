SHELL:=/bin/bash
docker_compose_dev = docker-compose --project-directory docker/dev -f docker/dev/docker-compose.yml

## Common ##

dev-build:
	$(docker_compose_dev) build

# Start the UI
dev-up: 
	$(docker_compose_dev) up --build -d

# Start without rebuilding the Docker image
# (use when dependencies have not changed for faster starts).
dev-up-no-build: 
	$(docker_compose_dev) up -d

# Stop the UI
dev-down:
	$(docker_compose_dev) down

dev-down-remove-orphans:
	$(docker_compose_dev) down --remove-orphans

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

odc-db-ssh:
	docker exec -it odc-db bash

## End Common ##

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

# Create the ODC database Docker container.
create-odc-db:
	docker run -d \
	-e POSTGRES_DB=datacube \
	-e POSTGRES_USER=dc_user \
	-e POSTGRES_PASSWORD=localuser1234 \
	--name=odc-db \
	--network="odc" \
	-v odc-db-vol:/var/lib/postgresql/data \
	postgres:10-alpine

start-odc-db:
	docker start odc-db

stop-odc-db:
	docker stop odc-db

restart-odc-db: stop-odc-db start-odc-db

delete-odc-db:
	docker rm odc-db

## End ODC DB ##

## Django DB ##

# Create the persistent volume for the Django database.
dev-create-django-db-volume:
	docker volume create django-db-vol

# Delete the persistent volume for the Django database.
dev-delete-django-db-volume:
	docker volume rm django-db-vol

## End Django DB ##

sudo-ubuntu-install-docker:
	sudo apt-get update
	sudo apt install -y docker.io docker-compose
	sudo systemctl start docker
	sudo systemctl enable docker
	# The following steps are for enabling use 
	# of the `docker` command for the current user
	# without using `sudo`
	getent group docker || sudo groupadd docker
	sudo usermod -aG docker ${USER}
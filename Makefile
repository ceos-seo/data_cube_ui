SHELL:=/bin/bash

# List the running containers.
dev-ps:
	docker-compose --project-directory docker \
	-f docker/docker-compose.dev.yml ps

# Start the UI.
dev-up: 
	docker-compose --project-directory docker \
	-f docker/docker-compose.dev.yml up --build -d

# Stop the UI.
dev-down:
	docker-compose --project-directory docker \
	-f docker/docker-compose.dev.yml down

# Start the UI without rebuilding the UI Docker image
# (use when appropriate for faster starts).
dev-up-no-build: 
	docker-compose --project-directory docker \
	-f docker/docker-compose.dev.yml up -d

# Connect to the running UI container.
dev-ssh:
	docker-compose --project-directory docker \
	-f docker/docker-compose.dev.yml exec ui bash

# Create the persistent volume for the Django database.
dev-create-django-db-volume:
	docker volume create django-db-vol

# Delete the persistent volume for the Django database.
dev-delete-django-db-volume:
	docker volume rm django-db-vol

# Create the `odc` network on which everything runs.
create-odc-network:
	docker network create odc

# Create the persistent volume for the Django database.
create-odc-db-volume:
	docker volume create odc-db

# Delete the persistent volume for the Django database.
delete-odc-db-volume:
	docker volume rm odc-db

# Create the ODC database.
create-odc-db:
	docker run -d \
	-e POSTGRES_DB=datacube \
	-e POSTGRES_USER=dc_user \
	-e POSTGRES_PASSWORD=localuser1234 \
	--name=odc-db \
	--network="odc" \
	-v odc-db:/var/lib/postgresql/data \
	postgres:10-alpine

delete-odc-db:
	docker container stop odc-db
	docker container rm odc-db

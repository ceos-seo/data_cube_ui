#!/bin/sh
# DEBIAN_FRONTEND=noninteractive apt-get install -y \
#     redis-tools \
#     postgresql-client \
#     libpq-dev
DEBIAN_FRONTEND=noninteractive apt-get install -y \
    redis-tools
DEBIAN_FRONTEND=noninteractive apt-get install -y \
    postgresql-client
DEBIAN_FRONTEND=noninteractive apt-get install -y \
    libpq-dev
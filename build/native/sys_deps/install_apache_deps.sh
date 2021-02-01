#!/bin/sh
DEBIAN_FRONTEND=noninteractive apt-get install -y \
    apache2 \
    libapache2-mod-wsgi-py3
    # Needed for the `a2dissite` and `a2ensite` commands.
    # python3-dev
    # devscripts \
    # dpkg-dev
    # debhelper \
    # lsb-release \
    # libaprutil1-dev \

# apt-get build-dep apache2

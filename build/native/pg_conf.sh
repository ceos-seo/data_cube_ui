#!/bin/sh
echo \
"${DJANGO_DB_HOSTNAME}:5432:"\
"${DJANGO_DB_DATABASE}:${DJANGO_DB_USER}:"\
"${DJANGO_DB_PASSWORD}" > config/.pgpass
echo \
"${ODC_DB_HOSTNAME}:${ODC_DB_PORT}:"\
"${ODC_DB_DATABASE}:${ODC_DB_USER}:"\
"${ODC_DB_PASSWORD}" >> config/.pgpass
cp config/.pgpass /var/www/.pgpass
chmod 600 /var/www/.pgpass

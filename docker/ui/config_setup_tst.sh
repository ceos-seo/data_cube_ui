#!/bin/sh

# # (dev) Change the Apache UID and GID to match
# # the owner of the UI directory.
# if [ "$ENVIRONMENT" = "DEV" ]; then
#   # If the UID or GID are not supplied, determine them
#   # from the owner of the UI directory.
#   if [ "$APACHE_UID" = "" ]; then
#     export APACHE_UID=$(stat -c '%u' .)
#   fi
#   usermod -u $APACHE_UID www-data
# fi

# # Start the Apache web server.
# service apache2 start

# # Wait for the databases to start.
# until PGPASSWORD=$DJANGO_DB_PASSWORD psql -h "$DJANGO_DB_HOSTNAME" -U "$DJANGO_DB_USER" $DJANGO_DB_DATABASE -c '\q'; do
#   >&2 echo "Django database is inaccessible - sleeping"
#   sleep 1
# done
# >&2 echo "Django database is accessible."

# until PGPASSWORD=$ODC_DB_PASSWORD psql -h "$ODC_DB_HOSTNAME" -U "$ODC_DB_USER" $ODC_DB_DATABASE -c '\q'; do
#   >&2 echo "ODC database is inaccessible - sleeping"
#   sleep 1
# done
# >&2 echo "ODC database is accessible."

exec "$@"
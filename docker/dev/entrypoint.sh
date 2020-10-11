#!/bin/bash

# (dev) Change the Apache UID to match
# the owner of the apps directory (using volumes).
if [ "$ENVIRONMENT" = "DEV" ]; then
  # If the UID is not supplied, determine it
  # from the owner of the apps directory.
  if [ "$APACHE_UID" = "" ]; then
    export APACHE_UID=$(stat -c '%u' apps)
  fi
  usermod -u $APACHE_UID www-data
  # Own directories created during build.
  chown www-data:www-data ${WORKDIR}
  if [[ "$(stat -c '%u' ${WORKDIR}/datacube_env)" != $APACHE_UID ]]; then
    chown -R www-data:www-data ${WORKDIR}/datacube_env
  fi
  if [[ "$(stat -c '%u' /datacube/ui_results)" != $APACHE_UID ]]; then
    chown -R www-data:www-data /datacube/ui_results
  fi
  if [[ "$(stat -c '%u' config/datacube.conf)" != $APACHE_UID ]]; then
    chown -R www-data:www-data config
  fi
  # Apache and Celery dirs.
  if [[ "$(stat -c '%u' /etc/apache2/sites-available/)" != $APACHE_UID ]]; then
    chown -R www-data:www-data /etc/apache2/sites-available/
  fi
  if [[ "$(stat -c '%u' /etc/default)" != $APACHE_UID ]]; then
    chown -R www-data:www-data /etc/default
  fi
  if [[ "$(stat -c '%u' /etc/init.d)" != $APACHE_UID ]]; then
    chown -R www-data:www-data /etc/init.d
  fi
  
  # Make the Apache user a sudoer with no password required.
  echo "www-data ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers
fi

# Start Apache.
service apache2 start

# Initialize ODC and the database.
source datacube_env/bin/activate
datacube system init

# Start the Celery workers and scheduler.
/etc/init.d/data_cube_ui start
chmod 777 /var/log/celery/ /var/run/celery/
# The celerybeat service runs as root and expects the directory
# for its pid file (/var/run/celery) to be owned by root.
chown root:root /var/log/celery/ /var/run/celery/
/etc/init.d/celerybeat start

# Wait for the databases to start.
until PGPASSWORD=$DJANGO_DB_PASSWORD psql -h "$DJANGO_DB_HOSTNAME" -U "$DJANGO_DB_USER" $DJANGO_DB_DATABASE -c '\q'; do
  >&2 echo "Django database is inaccessible - sleeping"
  sleep 1
done
>&2 echo "Django database is accessible."

until PGPASSWORD=$ODC_DB_PASSWORD psql -h "$ODC_DB_HOSTNAME" -U "$ODC_DB_USER" $ODC_DB_DATABASE -c '\q'; do
  >&2 echo "ODC database is inaccessible - sleeping"
  sleep 1
done
>&2 echo "ODC database is accessible."

exec "$@"
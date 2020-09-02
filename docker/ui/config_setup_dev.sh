#!/bin/sh

# Create a postfix mail server if an admin email address
# was supplied as an environment variable.
# if [ -n "${ADMIN_EMAIL}" ];
# then
#   debconf-set-selections < "postfix postfix/mailname string your.hostname.com" && \
#   debconf-set-selections < "postfix postfix/main_mailer_type string 'Internet Site'"
#   DEBIAN_FRONTEND=noninteractive apt-get install -y postfix mailutils

#   cat <<- EOF > /etc/postfix/main.cf
#   myhostname = $hostname
#   mailbox_size_limit = 0
#   recipient_delimiter = +
#   inet_interfaces = localhost
# EOF
#   service postfix restart;
# fi

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
  if [[ "$(stat -c '%u' ${WORKDIR}/datacube_env)" = $APACHE_UID ]]; then
    chown -R www-data:www-data ${WORKDIR}/datacube_env
  fi
  if [[ "$(stat -c '%u' /datacube/ui_results)" = $APACHE_UID ]]; then
    chown -R www-data:www-data /datacube/ui_results
  fi
  if [[ "$(stat -c '%u' config/datacube.conf)" = $APACHE_UID ]]; then
    chown -R www-data:www-data config
  fi
  # deluser www-data sudo # remove sudo permissions
fi

# DEV - Make the Apache user a sudoer with no password required.
echo "www-data ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers

su - www-data
cd /app

# Initialize ODC and the database.
source datacube_env/bin/activate
datacube system init

# Start the Celery workers and scheduler.
/etc/init.d/data_cube_ui start
chmod 777 /var/log/celery/ /var/run/celery/
chown root:root /var/log/celery/ /var/run/celery/
/etc/init.d/celerybeat start

# Start the Apache web server.
service apache2 start

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

# Perform Django migrations.
bash scripts/migrations.sh

exec "$@"
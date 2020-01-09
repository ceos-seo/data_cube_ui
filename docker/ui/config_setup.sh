#!/bin/sh

# Create a postfix mail server if an admin email address
# was supplied as an environment variable.
if [ -n "${ADMIN_EMAIL}" ];
then
  debconf-set-selections < "postfix postfix/mailname string your.hostname.com" && \
  debconf-set-selections < "postfix postfix/main_mailer_type string 'Internet Site'"
  DEBIAN_FRONTEND=noninteractive apt-get install -y postfix mailutils

  cat <<- EOF > /etc/postfix/main.cf
  myhostname = $hostname
  mailbox_size_limit = 0
  recipient_delimiter = +
  inet_interfaces = localhost
EOF
  service postfix restart;
fi

## Setup the Open Data Cube configuration.
#cat <<- EOF > $WORKDIR/config/.datacube.conf
#[datacube]
#db_hostname: $DB_HOSTNAME
#db_database: $DB_DATABASE
#db_username: $DB_USER
#db_password: $DB_PASSWORD
#EOF
#cp $WORKDIR/config/.datacube.conf /etc/.datacube.conf

## Setup the Apache configuration.
#sed -i "s/localuser/$(id -un)/g" config/dc_ui.conf
#cp $WORKDIR/config/dc_ui.conf /etc/apache2/sites-available/dc_ui.conf
#a2dissite 000-default.conf
#a2ensite dc_ui.conf
#service apache2 reload

## Postgres pgpass configuration.
#echo "${DB_HOSTNAME}:${DB_PORT}:${DB_DATABASE}:${DB_USER}:${DB_PASSWORD}" > config/.pgpass
#cp config/.pgpass ~/.pgpass
#chmod 600 ~/.pgpass

# Wait for Postgres to start.
until PGPASSWORD=$DB_PASSWORD psql -h "$DB_HOSTNAME" -U "$DB_USER" $DB_DATABASE -c '\q'; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done

>&2 echo "Postgres is running."

# Perform Django migrations and initial data import.
python3 manage.py makemigrations {accounts,cloud_coverage,coastal_change,custom_mosaic_tool,data_cube_manager,dc_algorithm,fractional_cover,slip,spectral_anomaly,spectral_indices,task_manager,tsm,urbanization,water_detection,data_cube_ui}
python3 manage.py makemigrations
python3 manage.py migrate
python3 manage.py loaddata db_backups/init_database.json

exec "$@"
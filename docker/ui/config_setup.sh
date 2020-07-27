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

# (dev) Change the Apache UID and GID to match
# the owner of the UI directory.
if [ "$ENVIRONMENT" = "DEV" ]; then
  # If the UID or GID are not supplied, determine them
  # from the owner of the UI directory.
  if [ "$APACHE_UID" = "" ]; then
    export APACHE_UID=$(stat -c '%u' .)
    echo "$APACHE_UID" > uid.txt
  fi
  usermod -u $APACHE_UID www-data
fi

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

exec "$@"
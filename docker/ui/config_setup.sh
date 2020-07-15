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

# Wait for Postgres to start.
until PGPASSWORD=$DB_PASSWORD psql -h "$DB_HOSTNAME" -U "$DB_USER" $DB_DATABASE -c '\q'; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done

>&2 echo "Postgres is running."

exec "$@"
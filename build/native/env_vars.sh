APACHE_USER_PATH=$(su - www-data -c 'echo $PATH')
NEW_APACHE_USER_PATH=$PATH:$APACHE_USER_PATH

# /var/www/.profile #
echo "export PATH=${NEW_APACHE_USER_PATH}" >> /var/www/.profile && \
echo "export ADMIN_EMAIL=${ADMIN_EMAIL}" >> /var/www/.profile && \
echo "export ODC_DB_HOSTNAME=${ODC_DB_HOSTNAME}" >> /var/www/.profile && \
echo "export ODC_DB_DATABASE=${ODC_DB_DATABASE}" >> /var/www/.profile && \
echo "export ODC_DB_USER=${ODC_DB_USER}" >> /var/www/.profile && \
echo "export ODC_DB_PASSWORD=${ODC_DB_PASSWORD}" >> /var/www/.profile && \
echo "export ODC_DB_PORT=${ODC_DB_PORT}" >> /var/www/.profile && \
echo "export DATACUBE_CONFIG_PATH=${DATACUBE_CONFIG_PATH}" >> /var/www/.profile && \
echo "export DJANGO_DB_HOSTNAME=${DJANGO_DB_HOSTNAME}" >> /var/www/.profile && \
echo "export DJANGO_DB_DATABASE=${DJANGO_DB_DATABASE}" >> /var/www/.profile && \
echo "export DJANGO_DB_USER=${DJANGO_DB_USER}" >> /var/www/.profile && \
echo "export DJANGO_DB_PASSWORD=${DJANGO_DB_PASSWORD}" >> /var/www/.profile && \
echo "export REDIS_HOST=${REDIS_HOST}" >> /var/www/.profile && \
# (LC_ALL, LANG) Avoid complaints from the click library when using python3.
echo "export LC_ALL=C.UTF-8" >> /var/www/.profile && \
echo "export LANG=C.UTF-8" >> /var/www/.profile && \
echo "export MPLCONFIGDIR=${MPLCONFIGDIR}" >> /var/www/.profile && \
echo "export DC_UI_DIR=${DC_UI_DIR}" >> /var/www/.profile && \
# AWS credentials
echo "export AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}" >> /var/www/.profile && \
echo "export AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}" >> /var/www/.profile && \
echo "export AWS_DEFAULT_REGION=${AWS_DEFAULT_REGION}" >> /var/www/.profile && \
# /etc/apache2/envvars #
echo "export PATH=${NEW_APACHE_USER_PATH}" >> /etc/apache2/envvars && \
echo "export ADMIN_EMAIL=${ADMIN_EMAIL}" >> /etc/apache2/envvars && \
echo "export ODC_DB_HOSTNAME=${ODC_DB_HOSTNAME}" >> /etc/apache2/envvars && \
echo "export ODC_DB_DATABASE=${ODC_DB_DATABASE}" >> /etc/apache2/envvars && \
echo "export ODC_DB_USER=${ODC_DB_USER}" >> /etc/apache2/envvars && \
echo "export ODC_DB_PASSWORD=${ODC_DB_PASSWORD}" >> /etc/apache2/envvars && \
echo "export ODC_DB_PORT=${ODC_DB_PORT}" >> /etc/apache2/envvars && \
echo "export DATACUBE_CONFIG_PATH=${DATACUBE_CONFIG_PATH}" >> /etc/apache2/envvars && \
echo "export DJANGO_DB_HOSTNAME=${DJANGO_DB_HOSTNAME}" >> /etc/apache2/envvars && \
echo "export DJANGO_DB_DATABASE=${DJANGO_DB_DATABASE}" >> /etc/apache2/envvars && \
echo "export DJANGO_DB_USER=${DJANGO_DB_USER}" >> /etc/apache2/envvars && \
echo "export DJANGO_DB_PASSWORD=${DJANGO_DB_PASSWORD}" >> /etc/apache2/envvars && \
echo "export REDIS_HOST=${REDIS_HOST}" >> /etc/apache2/envvars && \
echo "export LC_ALL=C.UTF-8" >> /etc/apache2/envvars && \
echo "export LANG=C.UTF-8" >> /etc/apache2/envvars && \
echo "export MPLCONFIGDIR=${MPLCONFIGDIR}" >> /etc/apache2/envvars && \
echo "export DC_UI_DIR=${DC_UI_DIR}" >> /etc/apache2/envvars && \
# AWS credentials
echo "export AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}" >> /etc/apache2/envvars && \
echo "export AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}" >> /etc/apache2/envvars && \
echo "export AWS_DEFAULT_REGION=${AWS_DEFAULT_REGION}" >> /etc/apache2/envvars
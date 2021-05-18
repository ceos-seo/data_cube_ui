ARG BASE_IMG
FROM $BASE_IMG

COPY build/native/sys_deps/install_dev_deps.sh build/native/sys_deps/install_dev_deps.sh
RUN build/native/sys_deps/install_dev_deps.sh

ARG WORKDIR=/app
ENV WORKDIR=${WORKDIR}
ARG DC_UI_DIR=${WORKDIR}
ENV DC_UI_DIR=${DC_UI_DIR}

# Setup the ODC configuration.
COPY build/native/odc_conf.sh build/native/odc_conf.sh

# Setup the Apache configuration.
ARG DC_UI_PYTHONHOME
ARG DC_UI_PYTHONPATH
ENV DC_UI_PYTHONHOME=/miniconda/envs/odc \
    DC_UI_PYTHONPATH=${DC_UI_DIR}
COPY config/templates/dc_ui.conf config/templates/dc_ui.conf
ENV ODC_DB_HOSTNAME \
    ODC_DB_DATABASE \
    ODC_DB_USER \
    ODC_DB_PASSWORD \
    ODC_DB_PORT
COPY build/native/apache_conf.sh build/native/apache_conf.sh

# Postgres pgpass configuration.
ENV DJANGO_DB_HOSTNAME \
    DJANGO_DB_DATABASE \
    DJANGO_DB_USER \
    DJANGO_DB_PASSWORD
COPY build/native/pg_conf.sh build/native/pg_conf.sh

# Setup Celery
COPY config/templates/celeryd_conf config/templates/celeryd_conf
COPY config/celeryd config/celeryd
COPY config/templates/celerybeat_conf config/templates/celerybeat_conf
COPY config/celerybeat config/celerybeat
COPY build/native/celery_conf.sh build/native/celery_conf.sh

# Set environment variables for Apache.
ENV REDIS_HOST=${REDIS_HOST}
ARG MPLCONFIGDIR
ENV MPLCONFIGDIR=${MPLCONFIGDIR}
ENV AWS_ACCESS_KEY_ID \
    AWS_SECRET_ACCESS_KEY \
    AWS_DEFAULT_REGION

ENV NEW_APACHE_USER_PATH=''
COPY build/native/env_vars.sh build/native/env_vars.sh

COPY build/native/export_path.sh build/native/export_path.sh
RUN build/native/export_path.sh

# Setup the entrypoint script.
COPY build/native/entrypoint.sh build/native/entrypoint.sh
ENV ENVIRONMENT="DEV" \
    APACHE_UID=""
RUN chmod 555 -R build
ENTRYPOINT ["build/native/entrypoint.sh"]

WORKDIR $WORKDIR

# Sleep to keep the container from exiting so we can `exec` it.
CMD ["tail", "-f", "/dev/null"]

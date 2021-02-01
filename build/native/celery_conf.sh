#!/bin/bash
cp config/templates/celeryd_conf config/celeryd_conf && \
sed -i "s#\${DC_UI_DIR}#${DC_UI_DIR}#g" config/celeryd_conf && \
sed -i "s#\${DC_UI_PYTHONHOME}#${DC_UI_PYTHONHOME}#g" config/celeryd_conf && \
cp config/celeryd_conf /etc/default/data_cube_ui && \
chmod 644 /etc/default/data_cube_ui

cp config/celeryd /etc/init.d/celeryd
chmod 777 /etc/init.d/celeryd
cp config/celeryd /etc/init.d/data_cube_ui
chmod 777 /etc/init.d/data_cube_ui

cp config/templates/celerybeat_conf config/celerybeat_conf
sed -i "s#\${DC_UI_DIR}#${DC_UI_DIR}#g" config/celerybeat_conf && \
sed -i "s#\${DC_UI_PYTHONHOME}#${DC_UI_PYTHONHOME}#g" config/celerybeat_conf && \
cp config/celerybeat_conf /etc/default/celerybeat && \
chmod 644 /etc/default/celerybeat

cp config/celerybeat /etc/init.d/celerybeat && \
chmod 777 /etc/init.d/celerybeat

chown -R root:root /etc/default /etc/init.d

cp config/templates/dc_ui.conf config/dc_ui.conf
sed -i "s#\${DC_UI_DIR}#${DC_UI_DIR}#g" config/dc_ui.conf
sed -i "s#\${DC_UI_PYTHONHOME}#${DC_UI_PYTHONHOME}#g" config/dc_ui.conf
sed -i "s#\${DC_UI_PYTHONPATH}#${DC_UI_PYTHONPATH}#g" config/dc_ui.conf
sed -i "s#\${DC_UI_DIR}#${DC_UI_DIR}#g" config/dc_ui.conf
sed -i "s#\${DJANGO_DB_HOSTNAME}#${DJANGO_DB_HOSTNAME}#g" config/dc_ui.conf
sed -i "s#\${ODC_DB_HOSTNAME}#${ODC_DB_HOSTNAME}#g" config/dc_ui.conf
cp config/dc_ui.conf /etc/apache2/sites-available/dc_ui.conf
# cp /etc/apache2/sites-available/dc_ui.conf /etc/apache2/apache2.conf
# Disable the default Apache config and enable the new one.
a2dissite 000-default.conf
a2ensite dc_ui.conf
# Set Apache to start on system boot.
update-rc.d apache2 defaults
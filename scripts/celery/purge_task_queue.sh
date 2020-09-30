python3 manage.py shell -c \
    "from data_cube_ui.celery_app import app;\
     app.control.purge()"
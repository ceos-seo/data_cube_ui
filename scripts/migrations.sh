#!/usr/bin/bash

python3 manage.py makemigrations
python3 manage.py makemigrations \
    accounts cloud_coverage coastal_change \
    custom_mosaic_tool data_cube_manager dc_algorithm \
    fractional_cover spectral_anomaly \
    spectral_indices task_manager tsm urbanization \
    water_detection data_cube_ui
python3 manage.py migrate

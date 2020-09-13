#!/usr/bin/bash
if [ $# -ne 1 ]; then
    echo "Must supply output path (JSON) as argument."
    exit 1
fi
python3 manage.py dumpdata \
    accounts cloud_coverage coastal_change custom_mosaic_tool dc_algorithm \
    fractional_cover spectral_anomaly spectral_indices task_manager tsm urbanization \
    water_detection data_cube_ui > $1 --indent 2

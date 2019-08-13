#!/usr/bin/bash
python manage.py dumpdata cloud_coverage coastal_change custom_mosaic_tool dc_algorithm fractional_cover ndvi_anomaly slip spectral_anomaly spectral_indices tsm urbanization water_detection > db_backups/init_database.json --indent 2

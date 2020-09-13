#!/usr/bin/bash
if [ $# -ne 1 ]; then
    echo "Must supply input path (JSON) as argument."
    exit 1
fi
python3 manage.py loaddata $1
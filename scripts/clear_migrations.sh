#!/usr/bin/bash
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete 
find . -path "*/migrations/*.pyc"  -delete
#!/bin/bash
python3 -m pip install --user -r requirements.txt
python3 manage.py collectstatic --no-input
python3 manage.py migrate
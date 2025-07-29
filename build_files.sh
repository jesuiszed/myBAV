#!/bin/bash
export PATH=$PATH:/vercel/.local/bin
apt-get update && apt-get install -y libsqlite3-dev
python3 -m pip install --user -r requirements.txt
python3 manage.py collectstatic --no-input
python3 manage.py migrate
#!/bin/sh
set -e
pwd
echo "Running initcouchdb..."
python manage.py initcouchdb
echo "Running uwsgi..."
uwsgi uwsgi.yml
#!/bin/sh
set -e
python /code/manage.py initcouchdb
uwsgi /code/uwsgi.yml
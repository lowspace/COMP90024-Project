#!/bin/sh
set -e
echo "Container's IP address: `awk 'END{print $1}' /etc/hosts`"
python /code/manage.py initcouchdb
uwsgi /code/uwsgi.yml
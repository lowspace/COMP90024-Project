#!/bin/bash
uwsgi uwsgi.yml &
sleep 30
python3 manage.py process_tasks &
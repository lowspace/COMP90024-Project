#!/bin/bash
uwsgi uwsgi.yml &
sleep 30
printenv | grep DJANGO | tee -a /etc/environment
crontab ./cron
FROM python:3.6-alpine3.12

# Create a group and user to run our app
RUN adduser -S appuser -G root

# Add project code
RUN mkdir /code/
WORKDIR /code/
ADD . /code/


# Packages
RUN apk update;
RUN apk add linux-headers gcc libc-dev curl openjdk8 geos musl-dev python3-dev bash vim;
RUN pip install --no-cache --upgrade pip 
RUN pip install --no-cache-dir -r requirements.txt

ENV DJANGO_SETTINGS_MODULE=twitterlance.settings
ENV HTTP_PROXY=http://wwwproxy.unimelb.edu.au:8000/
ENV HTTPS_PROXY=http://wwwproxy.unimelb.edu.au:8000/
ENV http_proxy=http://wwwproxy.unimelb.edu.au:8000/
ENV https_proxy=http://wwwproxy.unimelb.edu.au:8000/
ENV no_proxy=couchdb,localhost,127.0.0.1,localaddress,172.16.0.0/12,.melbourne.rc.nectar.org.au,.storage.unimelb.edu.au,.cloud.unimelb.edu.au

# uWSGI listening on this port
EXPOSE 80

# Create and apply cron job for django analyser jobs
COPY crontab /etc/cron.d/cjob
RUN chmod 0644 /etc/cron.d/cjob
RUN touch /etc/environment
RUN chmod 0664 /etc/environment
RUN touch /var/log/cron.log
RUN crontab /etc/cron.d/cjob

# Service launcher
RUN mkdir -p /var/log/supervisor
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

ENTRYPOINT /bin/sh -c "printenv | tee -a /etc/environment && supervisord"
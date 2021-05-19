FROM python:3.6-alpine3.12

# Create a group and user to run our app
RUN adduser -S appuser -G root

# Add project code
RUN mkdir /code/
WORKDIR /code/
ADD . /code/

ENV DJANGO_SETTINGS_MODULE=twitterlance.settings

# Packages
RUN apk update;
RUN apk add linux-headers gcc libc-dev curl openjdk8 geos musl-dev python3-dev bash vim;
RUN pip install --no-cache --upgrade pip 
RUN pip install --no-cache-dir -r requirements.txt


# uWSGI listening on this port
EXPOSE 80

# Create and apply cron job for django analyser jobs
COPY crontab /etc/cron.d/cjob
RUN chmod 0644 /etc/cron.d/cjob
RUN touch /etc/environment
RUN chmod 0664 /etc/environment
RUN touch /var/log/cron.log
RUN crontab /etc/cron.d/cjob

RUN mkdir -p /var/log/supervisor

COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

ENTRYPOINT /bin/sh -c "printenv | grep DJANGO | tee -a /etc/environment && supervisord"
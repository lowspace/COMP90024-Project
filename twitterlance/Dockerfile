FROM ubuntu:18.04

# Create a group and user to run our app
RUN adduser appuser
RUN usermod -a -G root appuser

# Add project code
RUN mkdir /code/
WORKDIR /code/
ADD . /code/

ENV DJANGO_SETTINGS_MODULE=twitterlance.settings


RUN apt-get update; \
    apt-get install -y apt-utils \
        gcc \
        libc-dev \
        curl \
        openjdk-8-jdk \
        python3.8 \ 
        cron \
        supervisor \
        python3-pip;

RUN pip3 install -r requirements.txt;

# uWSGI listening on this port
EXPOSE 80

# Create cron job
COPY crontab /etc/cron.d/cjob
RUN chmod 0644 /etc/cron.d/cjob
RUN chmod 0664 /etc/environment
RUN printenv | grep DJANGO >> /etc/environment
RUN touch /var/log/cron.log
# Apply cron job
RUN crontab /etc/cron.d/cjob

RUN mkdir -p /var/log/supervisor
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf
ENTRYPOINT ["/usr/bin/supervisord"]
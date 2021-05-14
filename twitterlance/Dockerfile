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
        python3-pip;

RUN pip3 install -r requirements.txt;

# uWSGI listening on this port
EXPOSE 80

# To run the app on the app user
USER appuser

# Initialisation
ENTRYPOINT ["uwsgi", "uwsgi.yml"]
FROM python:3.7-alpine

# Create a group and user to run our app
RUN adduser -S appuser -G root

# Add project code
RUN mkdir /code/
WORKDIR /code/
ADD . /code/

ENV DJANGO_SETTINGS_MODULE=twitterlance.settings

RUN apk update

# Python dependencies
RUN set -e; \
	apk add --no-cache --virtual .build-deps \
		gcc \
		libc-dev \
		linux-headers \
	; \
	pip install -r requirements.txt; \
	apk del .build-deps;

RUN apk add --no-cache --virtual mailcap

# uWSGI listening on this port
EXPOSE 80

# To run the app on the app user
USER appuser

# Initialisation
ENTRYPOINT ["uwsgi", "uwsgi.yml"]
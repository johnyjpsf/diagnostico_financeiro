FROM python:3.8-slim

ENV CONTAINER_HOME=/var/www

ADD . $CONTAINER_HOME

WORKDIR $CONTAINER_HOME

RUN pip install --cert ssl-atsi.decea.intraer.pem --no-cache-dir -r $CONTAINER_HOME/requirements.txt

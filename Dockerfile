FROM python:3-alpine

RUN apk update

RUN apk add --virtual deps gcc python-dev linux-headers musl-dev postgresql-dev

RUN apk add libpq

RUN pip install requests pymongo psutil

ADD . /tgt_grease_core

WORKDIR /tgt_grease_core

RUN python ./setup.py install

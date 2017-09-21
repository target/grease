FROM python:2.7

RUN pip install psycopg2 requests pymongo

ADD . /tgt_grease_core

WORKDIR /tgt_grease_core

RUN python ./setup.py install

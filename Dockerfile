FROM python:2.7

RUN pip install requests pymongo psutil

ADD . /tgt_grease_core

WORKDIR /tgt_grease_core

RUN python ./setup.py install

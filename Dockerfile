FROM ubuntu:16.04

RUN apt-get update \
    && apt-get install -y python python-pip \
    && pip install azure-batch

COPY scale_pools.py /
RUN chmod a+x /scale_pools.py
ENTRYPOINT ["/scale_pools.py"]
CMD []

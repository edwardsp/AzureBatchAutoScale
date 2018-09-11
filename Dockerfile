FROM alpine:3.8
MAINTAINER Paul Edwards <https://github.com/edwardsp/AzureBatchAutoScale>

RUN apk update  \
    && apk add --update --no-cache musl \
        musl build-base python3 python3-dev libressl-dev libffi-dev \
        ca-certificates git \
    && pip3 install azure-batch \
    && apk del --purge build-base python3-dev libressl-dev libffi-dev git \
    && rm /var/cache/apk/*

COPY scale_pools.py /
RUN chmod a+x /scale_pools.py
ENTRYPOINT ["/scale_pools.py"]

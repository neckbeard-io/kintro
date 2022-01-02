ARG PYTHON_VERSION
ARG PYTHON_BASE
ARG PYTHON_IMAGE=python:${PYTHON_VERSION}-${PYTHON_BASE}
FROM ${PYTHON_IMAGE}

ENV PYTHON_VERSION=${PYTHON_VERSION}

ARG KINTRO_REPO=https://github.com/brutog/kintro.git
ARG KINTRO_BRANCH=master

# SLOWISH
RUN apk add gcc \
            python3-dev \
            musl-dev \
            g++ \
	    git \
	    jq \
	    bash

RUN git clone ${KINTRO_REPO} kintro \
      && cd kintro \
      && git checkout ${KINTRO_BRANCH} \
      && pip install -e .

VOLUME ["/data"]

ENTRYPOINT ["kintro"]

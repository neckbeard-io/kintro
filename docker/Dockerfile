ARG PYTHON_VERSION
ARG PYTHON_BASE
ARG PYTHON_IMAGE=python:${PYTHON_VERSION}-${PYTHON_BASE}
FROM ${PYTHON_IMAGE} as kintro-base

ENV PYTHON_VERSION=${PYTHON_VERSION}

# SLOWISH
RUN apk add gcc \
            python3-dev \
            musl-dev \
            g++ \
	    git \
	    jq \
	    bash

VOLUME ["/data"]

ENTRYPOINT ["kintro"]



FROM kintro-base as kintro-repo

ARG KINTRO_REPO=https://github.com/neckbeard-io/kintro.git
ARG KINTRO_BRANCH=main

RUN git clone ${KINTRO_REPO} kintro \
      && cd kintro \
      && git checkout ${KINTRO_BRANCH} \
      && pip install -e .



FROM kintro-base as kintro-pkg

ARG KINTRO_VERSION=0.0.1rc1

RUN pip install kintro==${KINTRO_VERSION}

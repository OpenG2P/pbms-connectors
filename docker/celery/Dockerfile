# Celery image a cluster runs, for both the worker and the beat deployments.
# CELERY_APP on the pod selects which process starts.
# PBMS_VERSION must equal the openg2p-pbms-platform dependency version in
# helm/openg2p-pbms/Chart.yaml. Change both with scripts/bump-pbms-version.sh.
ARG PBMS_IMAGE=openg2p/openg2p-pbms-celery-base
ARG PBMS_VERSION=0.0.0-develop.18
FROM ${PBMS_IMAGE}:${PBMS_VERSION}

COPY extensions/registry-adapters /src/registry-adapters
RUN pip install --no-cache-dir --timeout 300 /src/registry-adapters

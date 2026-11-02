# Staff API image a cluster runs. Adds registry-adapters on the PBMS base.
# REGISTRY_ADAPTERS_CONNECTOR selects db or dci.
# PBMS_VERSION must equal the openg2p-pbms-platform dependency version in
# helm/openg2p-pbms/Chart.yaml. Change both with scripts/bump-pbms-version.sh.
ARG PBMS_IMAGE=openg2p/openg2p-pbms-staff-api-base
ARG PBMS_VERSION=0.0.0-develop.18
FROM ${PBMS_IMAGE}:${PBMS_VERSION}

COPY extensions/registry-adapters /src/registry-adapters
RUN pip install --no-cache-dir --timeout 300 /src/registry-adapters

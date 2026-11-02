# Odoo image a cluster runs. Adds the theme and registry addons on the PBMS base.
# PBMS_VERSION must equal the openg2p-pbms-platform dependency version in
# helm/openg2p-pbms/Chart.yaml. Change both with scripts/bump-pbms-version.sh.
ARG PBMS_IMAGE=openg2p/openg2p-pbms-odoo-base
ARG PBMS_VERSION=0.0.0-develop.18
FROM ${PBMS_IMAGE}:${PBMS_VERSION}

ARG EXTRA_ADDONS_DIR=/opt/odoo/extraaddons

USER root
COPY odoo/pbms_theme_extension ${EXTRA_ADDONS_DIR}/pbms-extensions/pbms_theme_extension
COPY odoo/g2p_registry_type_addon ${EXTRA_ADDONS_DIR}/pbms-extensions/g2p_registry_type_addon
COPY odoo/g2p_registry_addon ${EXTRA_ADDONS_DIR}/pbms-extensions/g2p_registry_addon
USER odoo

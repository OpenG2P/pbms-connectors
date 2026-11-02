# OpenG2P PBMS

Installs Programme & Beneficiary Management System into a namespace.

This chart depends on `openg2p-pbms-platform` and sets the Odoo, Celery, and staff API images. The beneficiary portal stays on the platform image. Worker and beat are two deployments of `openg2p-pbms-celery`; `CELERY_APP` selects the process.

Set `global.registryConnector` to `db` or `dci`. For `dci`, set `global.registryPartnerApiUrl` to the registry partner API.

# pbms-connectors

Domain extensions for PBMS: the Odoo registry models and the registry
connectors. Built as a thin layer over the
[pbms](https://github.com/OpenG2P/pbms) platform. pbms publishes the base images
and the `openg2p-pbms-platform` Helm chart; this repo adds the registry layer and
publishes the images and chart that a cluster runs.

## What this repo owns

| Path | Purpose |
|---|---|
| `odoo/` | `pbms_theme_extension`, `g2p_registry_type_addon`, `g2p_registry_addon` |
| `extensions/registry-adapters/` | Registry factory with FarmerDB, FarmerDCI, HouseholdDB, HouseholdDCI. `REGISTRY_ADAPTERS_CONNECTOR=db\|dci` selects the transport |
| `docker/` | Thin Dockerfiles (`FROM openg2p/openg2p-pbms-*-base`) for `openg2p-pbms-odoo`, `openg2p-pbms-celery`, `openg2p-pbms-staff-api` |
| `helm/openg2p-pbms/` | The chart you install. No templates: pins `openg2p-pbms-platform` and sets the three images |

## Platform pin

The pbms base image tag (`ARG PBMS_VERSION` in each Dockerfile) and the
`openg2p-pbms-platform` dependency version in `helm/openg2p-pbms/Chart.yaml` are
hardcoded and pinned together. `0.0.0-develop` is a placeholder that is never
published, so builds fail until the first real pin.

Run `./scripts/bump-pbms-version.sh -n` to see the version it would pick (writes
nothing). Run `./scripts/bump-pbms-version.sh` for the latest published develop
version, or `./scripts/bump-pbms-version.sh <version>` for a specific one. It
updates the Dockerfiles and the chart dependency together and only accepts a
version present in both the Helm index and Docker Hub. CI
(`test/test_pbms_pin_lockstep.py`) fails if they ever split.

## Versions

CI derives one version per commit for the three images and the chart:

| Ref | Version |
|---|---|
| `develop` | `0.0.0-develop.<n>` |
| branch `N.N` | `N.N.<patch>-rc.<n>` |
| tag `N.N.N` | `N.N.N` (promotes the RC images, no rebuild) |
| other branches | images only, no chart |

`openg2p-pbms` versions `3.0.0` and older, and `4.0.0-develop`, in the openg2p
Helm repo are the legacy chart that carried its own templates. Its values are not
under `pbms.`, so do not upgrade those installs in place. Cut releases of this
chart on a line above 4.0 (e.g. branch `4.1`, tag `4.1.0`) so they sort above the
legacy versions, and always pass `--version` for develop builds.

## Deploy

```bash
helm repo add openg2p https://openg2p.github.io/openg2p-helm
helm repo update
helm upgrade --install pbms openg2p/openg2p-pbms \
  --version <version> \
  --namespace <namespace> \
  --set global.keycloakBaseUrl=https://keycloak.example.org
```

The release name `pbms` is what Rancher shows under installed apps.

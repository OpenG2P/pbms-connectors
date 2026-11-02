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
| `extensions/registry-adapters/` | Registry factory with a DB and a DCI computation per register (farmer, household, disability). Each register picks its transport with `REGISTRY_ADAPTERS_<REGISTER>_CONNECTOR=db\|dci` and `REGISTRY_ADAPTERS_<REGISTER>_CONNECTION_STRING` |
| `docker/` | Thin Dockerfiles (`FROM openg2p/openg2p-pbms-*-base`) for `openg2p-pbms-odoo`, `openg2p-pbms-celery`, `openg2p-pbms-staff-api` |
| `helm/openg2p-pbms/` | The chart you install. No templates: pins `openg2p-pbms-platform` and sets the three images |

## Registers

Each register has a connector and a connection string, set in the chart under
`global.registers.<register>` (Rancher shows one group per register):

| Connector | Connection string |
|---|---|
| `db` | `postgresql://user:pass@host:5432/dbname` (percent-encode the password) |
| `dci` | The full search URL: `http(s)://host[:port]/dci/sync/search?reg_type=..&reg_record_type=..&timeout=30&ssl_verify=true` (query params optional) |

An empty connection string leaves the register unconfigured; only programs on
that register fail.

### Adding a register

1. Add the value to `G2PRegistryType` in both
   `extensions/registry-adapters/.../models/enum.py` and
   `odoo/g2p_registry_type_addon/models/registry_type.py`.
2. Add `computations/<register>.py` with two small classes on top of
   `RegistryDB` (set `model`, `payload`) and `RegistryDCI` (set `payload`,
   `reg_type`, `reg_record_type`, `match_field`, `fields`, `flat()`); see
   `computations/farmer.py`. Add its summaries mixin in `computations/_summary.py`
   and the `(DB, DCI)` pair in `registers.py`.
3. Add `global.registers.<register>` and its two `REGISTRY_ADAPTERS_*` lines in
   `helm/openg2p-pbms/values.yaml`.
4. Copy a register block in `helm/openg2p-pbms/questions.own.yaml`.
5. Add the Odoo model in `odoo/g2p_registry_addon`.

`test/test_register_config.py` fails CI if steps 1 to 4 disagree.

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

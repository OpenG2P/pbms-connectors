#!/usr/bin/env bash
# Bump the pinned openg2p-pbms-platform version this repo extends — in BOTH the
# Dockerfiles (ARG PBMS_VERSION) and the Helm chart dependency — atomically, so
# the two can never drift.
#
# WHY "SAFE" LATEST
#   The pbms repo publishes its base images and the openg2p-pbms-platform chart
#   in lockstep per commit, but the Helm index regenerates AFTER the images are
#   pushed, so there is a window where the newest image tag has no matching
#   chart yet. Picking an image-only version would write a chart dependency that
#   does not resolve. So "latest" here means the highest 0.0.0-develop.N present
#   in BOTH the Helm index AND on Docker Hub. An explicit version is likewise
#   verified to exist in both before anything is written.
#
# Requires: bash, curl, python3, helm. Run from the repo root.
set -euo pipefail

CHART_DIR="helm/openg2p-pbms"

PLATFORM_CHART="openg2p-pbms-platform"
HELM_INDEX="https://openg2p.github.io/openg2p-helm/index.yaml"
# One representative base image; the chart job only publishes after every
# pbms image built, so a version in the chart index has all four.
PROBE_IMAGE="openg2p/openg2p-pbms-celery-base"

die() { echo "ERROR: $*" >&2; exit 1; }
note() { echo "  $*"; }

usage() {
  cat <<EOF
Bump the pinned openg2p-pbms-platform version (Dockerfiles' ARG PBMS_VERSION +
the Helm chart dependency) atomically, so images and chart never drift.

Usage:
  ./scripts/bump-pbms-version.sh                 Bump to the latest SAFE version.
  ./scripts/bump-pbms-version.sh <version>       Bump to a specific version.
  ./scripts/bump-pbms-version.sh -n              Show the latest SAFE version;
  ./scripts/bump-pbms-version.sh -n <version>    check a version — write NOTHING.
  ./scripts/bump-pbms-version.sh -h              This help.

Options:
  -n, --check, --dry-run   Resolve/validate and print, but do not modify any file.
  -h, --help               Show this help.

"Latest SAFE" = the highest 0.0.0-develop.N present in BOTH the Helm index and
Docker Hub. A specific <version> (e.g. an RC or a release such as 4.1.0) is
accepted only if it exists in both.

Examples:
  ./scripts/bump-pbms-version.sh -n
  ./scripts/bump-pbms-version.sh
  ./scripts/bump-pbms-version.sh 0.0.0-develop.412
EOF
}

CHECK_ONLY=false
VERSION_ARG=""
while [ $# -gt 0 ]; do
  case "$1" in
    -h|--help)              usage; exit 0 ;;
    -n|--check|--dry-run)   CHECK_ONLY=true; shift ;;
    -*)                     die "unknown option '$1' (see --help)" ;;
    *)                      [ -z "$VERSION_ARG" ] || die "unexpected extra argument '$1'"; VERSION_ARG="$1"; shift ;;
  esac
done

command -v curl    >/dev/null || die "curl is required"
command -v python3 >/dev/null || die "python3 is required"
command -v helm    >/dev/null || die "helm is required"
[ -d "$CHART_DIR" ] || die "run from the repo root ($CHART_DIR not found)"

chart_versions() {
  curl -fsSL "$HELM_INDEX" 2>/dev/null \
    | grep -oE "${PLATFORM_CHART}-[0-9][^ ]*\.tgz" \
    | sed -E "s/^${PLATFORM_CHART}-//; s/\.tgz$//" | sort -u
}

image_versions() {
  local url="https://hub.docker.com/v2/repositories/${PROBE_IMAGE}/tags?page_size=100"
  while [ -n "$url" ] && [ "$url" != "null" ]; do
    local page; page=$(curl -fsSL "$url" 2>/dev/null) || break
    printf '%s' "$page" | python3 -c "import sys,json; d=json.load(sys.stdin); [print(t['name']) for t in d.get('results',[])]"
    url=$(printf '%s' "$page" | python3 -c "import sys,json; print(json.load(sys.stdin).get('next') or '')")
  done | sort -u
}

latest_safe() {
  python3 - "$@" <<'PY'
import sys
chart=set(l.strip() for l in open(sys.argv[1]) if l.strip())
image=set(l.strip() for l in open(sys.argv[2]) if l.strip())
both=[v for v in chart & image if v.startswith("0.0.0-develop.")]
if not both:
    sys.exit("no 0.0.0-develop.N version exists in BOTH the Helm index and Docker Hub")
both.sort(key=lambda v:int(v.rsplit(".",1)[1]))
print(both[-1])
PY
}

TMP=$(mktemp -d); trap 'rm -rf "$TMP"' EXIT
echo "Resolving published ${PLATFORM_CHART} versions…"
chart_versions > "$TMP/chart" || true
image_versions > "$TMP/image" || true
[ -s "$TMP/chart" ] || die "no ${PLATFORM_CHART} versions in the Helm index yet — merge pbms to develop and wait for its Build & Publish to go green"
[ -s "$TMP/image" ] || die "no tags for ${PROBE_IMAGE} on Docker Hub yet"

if [ -n "$VERSION_ARG" ]; then
  VERSION="$VERSION_ARG"
  grep -qxF "$VERSION" "$TMP/chart" || die "version '$VERSION' has no published ${PLATFORM_CHART} chart"
  grep -qxF "$VERSION" "$TMP/image" || die "version '$VERSION' has no published ${PROBE_IMAGE} image"
  note "requested version: $VERSION (verified in chart + images)"
else
  VERSION=$(latest_safe "$TMP/chart" "$TMP/image") || die "$VERSION"
  note "latest safe develop version (in chart + images): $VERSION"
fi

chart_pin() {
  python3 - "$CHART_DIR/Chart.yaml" <<'PY'
import re,sys
m=re.search(r'name:\s*openg2p-pbms-platform\b.*?version:\s*(\S+)', open(sys.argv[1]).read(), re.S)
print(m.group(1) if m else "")
PY
}
docker_pins() {
  grep -hoE 'ARG PBMS_VERSION=\S+' docker/*/Dockerfile | sed 's/ARG PBMS_VERSION=//' | sort -u | tr '\n' ',' | sed 's/,$//'
}

CUR_CHART=$(chart_pin)
CUR_DOCKER=$(docker_pins)
note "current: chart=$CUR_CHART  dockerfiles=$CUR_DOCKER"

if [ "$CUR_CHART" = "$VERSION" ] && [ "$CUR_DOCKER" = "$VERSION" ]; then
  note "already at $VERSION — nothing to do."
  exit 0
fi

if [ "$CHECK_ONLY" = "true" ]; then
  echo "  would bump: ${CUR_CHART} -> ${VERSION}   (run without -n to apply)"
  exit 0
fi

for f in docker/*/Dockerfile; do
  grep -q 'ARG PBMS_VERSION=' "$f" || continue
  python3 - "$f" "$VERSION" <<'PY'
import re,sys
f,v=sys.argv[1],sys.argv[2]
s=open(f).read()
s=re.sub(r'ARG PBMS_VERSION=\S+', f'ARG PBMS_VERSION={v}', s)
open(f,'w').write(s)
PY
done

python3 - "$CHART_DIR/Chart.yaml" "$VERSION" <<'PY'
import re,sys
f,v=sys.argv[1],sys.argv[2]
s=open(f).read()
# Rewrite the version ONLY inside the openg2p-pbms-platform dependency block.
def repl(m): return re.sub(r'(version:\s*)\S+', r'\g<1>'+v, m.group(0), count=1)
s=re.sub(r'-\s*name:\s*openg2p-pbms-platform\b.*?(?=\n\s*-\s|\n\S|\Z)', repl, s, count=1, flags=re.S)
open(f,'w').write(s)
PY

echo "Resolving the chart dependency…"
helm repo add openg2p https://openg2p.github.io/openg2p-helm >/dev/null 2>&1 || true
helm repo update openg2p >/dev/null 2>&1 || true
helm dependency update "$CHART_DIR" >/dev/null 2>&1 || die "helm dependency update failed for $VERSION"

NEW_CHART=$(chart_pin)
NEW_DOCKER=$(docker_pins)
[ "$NEW_CHART" = "$VERSION" ] && [ "$NEW_DOCKER" = "$VERSION" ] \
  || die "post-write check failed: chart=$NEW_CHART dockerfiles=$NEW_DOCKER (expected $VERSION)"

echo ""
echo "Bumped openg2p-pbms-platform pin: ${CUR_CHART} -> ${VERSION}"
echo "  Dockerfiles + chart dependency now aligned at ${VERSION}."
echo "  Review, then commit:"
echo "    git add docker ${CHART_DIR}/Chart.yaml && git commit"

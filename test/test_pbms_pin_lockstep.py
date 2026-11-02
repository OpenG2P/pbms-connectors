"""Guard: the openg2p-pbms-platform pin must be identical in every place it appears.

This repo extends ONE pbms version, used two ways:
  * the Docker base images — `ARG PBMS_VERSION=<v>` in every docker/*/Dockerfile
  * the Helm chart — the `openg2p-pbms-platform` dependency `version:` in Chart.yaml

If these drift, the images are built FROM one pbms base while the chart deploys
another platform's templates. `scripts/bump-pbms-version.sh` moves them
together; this test fails the build if anything ever splits them again.
"""

import pathlib
import re

import pytest

REPO = pathlib.Path(__file__).resolve().parent.parent
CHART = REPO / "helm" / "openg2p-pbms" / "Chart.yaml"


def _docker_pins():
    pins = {}
    for f in sorted((REPO / "docker").glob("*/Dockerfile")):
        m = re.search(r"^ARG PBMS_VERSION=(\S+)", f.read_text(), re.M)
        if m:
            pins[f.relative_to(REPO).as_posix()] = m.group(1)
    return pins


def _chart_pin():
    m = re.search(
        r"-\s*name:\s*openg2p-pbms-platform\b.*?version:\s*(\S+)",
        CHART.read_text(),
        re.S,
    )
    return m.group(1) if m else None


def test_pbms_pin_is_in_lockstep():
    docker = _docker_pins()
    chart = _chart_pin()
    assert docker, "no ARG PBMS_VERSION found in any docker/*/Dockerfile"
    assert chart, "no openg2p-pbms-platform dependency version found in Chart.yaml"

    all_pins = set(docker.values()) | {chart}
    if len(all_pins) != 1:
        lines = [f"  Chart.yaml openg2p-pbms-platform dependency: {chart}"]
        lines += [f"  {p}: {v}" for p, v in docker.items()]
        pytest.fail(
            "openg2p-pbms-platform pin has SPLIT — images and chart must be identical:\n"
            + "\n".join(lines)
            + "\n\nFix with: ./scripts/bump-pbms-version.sh <version>"
        )

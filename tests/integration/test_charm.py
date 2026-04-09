# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.

"""Integration tests for the Dashboard charm."""

import logging

import jubilant
import pytest
import requests
from tests.integration.types import App

logger = logging.getLogger(__name__)


def test_dashboard_health(dashboard_app: App, juju: jubilant.Juju) -> None:
    """
    arrange: Build and deploy the Dashboard charm.
    act: Do a get request to the main page and to an asset.
    assert: Both return 200 and the page contains the correct title.
    """
    status = juju.status()
    assert status.apps[dashboard_app.name].units[dashboard_app.name + "/0"].is_active
    for unit in status.apps[dashboard_app.name].units.values():
        url = f"http://{unit.address}:8000"
        res = requests.get(
            url,
            timeout=20,
        )
        assert res.status_code == 200
        assert b"<title>Home | Dashboard</title>" in res.content

        # Also some random thing from the static dir.
        url = f"http://{unit.address}:8000/static/dashboard.ico"
        res = requests.get(
            url,
            timeout=20,
        )
        assert res.status_code == 200


@pytest.mark.usefixtures("dashboard_app")
def test_dashboard_rq_worker_running(juju: jubilant.Juju, dashboard_app: App) -> None:
    """
    arrange: Build and deploy the Dashboard charm.
    act: Do a get request to the status api.
    assert: Check that there is one rq worker running.
    """
    status = juju.status()
    for unit in status.apps[dashboard_app.name].units.values():
        url = f"http://{unit.address}:8000/api/status/"
        res = requests.get(
            url,
            timeout=20,
        )
        assert res.status_code == 200
        assert res.json()["rq-workers-running"] == 1

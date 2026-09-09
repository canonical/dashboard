# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.

"""Integration tests for the Dashboard charm."""

import logging

import jubilant
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
        assert b"<title>Dashboard</title>" in res.content

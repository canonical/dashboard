# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.

"""Fixtures for the Dashboard charm tests."""

from pytest import Parser

DASHBOARD_IMAGE_PARAM = "--dashboard-image"


def pytest_addoption(parser: Parser) -> None:
    """Parse additional pytest options.

    Args:
        parser: Pytest parser.
    """
    parser.addoption(
        DASHBOARD_IMAGE_PARAM, action="store", help="Dashboard app image to be deployed"
    )
    parser.addoption("--kube-config", action="store", default="~/.kube/config")
    parser.addoption("--charm-file", action="store", help="Charm file to be deployed")
    parser.addoption("--localstack-address", action="store")
    parser.addoption("--model", action="store", help="Juju model to use instead of creating a temporary one")
    parser.addoption("--keep-models", action="store_true", default=False, help="Keep Juju models after tests")
    parser.addoption("--use-existing", action="store_true", default=False, help="Use existing Juju model")

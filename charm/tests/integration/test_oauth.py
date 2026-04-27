# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.

"""Integration tests for Oauth Integration."""

import json
import logging
import re
from urllib.parse import urlparse

import jubilant
import pytest
import requests
from playwright.sync_api import expect, sync_playwright

from tests.integration.types import App

logger = logging.getLogger(__name__)


# Pylint thinks there are too many local variables, but that's not true.
# pylint: disable=too-many-locals, unused-argument


@pytest.mark.usefixtures("identity_bundle")
@pytest.mark.usefixtures("browser_context_manager")
def test_oauth_integrations(
    juju: jubilant.Juju,
    dashboard_app: App,
    http: requests.Session,
):
    """
    arrange: set up the test Juju model and deploy the Dashboard charm.
    act: integrate with ingress and hydra.
    assert: the Dashboard charm uses the Kratos charm as the idp.
    """
    endpoint = "login"
    test_email = "test@example.com"
    test_password = "Testing1"
    test_username = "admin"
    test_secret = "secret_password"

    app = dashboard_app
    status = juju.status()

    # mypy things status.apps is possibly None, but if it's None, something is very wrong
    if not status.apps.get(app.name).relations.get("ingress"):  # type: ignore
        juju.integrate(f"{app.name}", "traefik-public")

    juju.wait(
        jubilant.all_active,
        timeout=15 * 60,
        delay=5,
    )

    if not status.apps.get(app.name).relations.get("oidc"):  # type: ignore
        juju.integrate(f"{app.name}", "hydra")

    juju.wait(
        jubilant.all_active,
        timeout=10 * 60,
        delay=5,
    )

    if not _admin_identity_exists(juju, test_email):
        juju.run(
            "kratos/0",
            "create-admin-account",
            {"email": test_email, "password": test_password, "username": test_username},
        )

    try:
        secret_id = juju.add_secret(test_secret, {"password": test_password})
    except jubilant.CLIError as e:
        if e.stderr != f'ERROR secret with name "{test_secret}" already exists\n':
            raise e
        secrets = json.loads(juju.cli("secrets", "--format", "json"))
        secret_id = [secret for secret in secrets if secrets[secret].get("name") == test_secret][0]

    juju.cli("grant-secret", secret_id, "kratos")
    result = juju.run(
        "kratos/0",
        "reset-password",
        {"email": test_email, "password-secret-id": secret_id.split(":")[-1]},
    )
    logger.info("results reset-password %s", result.results)

    res = json.loads(
        juju.run("traefik-public/0", "show-proxied-endpoints").results["proxied-endpoints"]
    )
    logger.info("result show-proxied %s", res)

    # make sure the app is alive
    response = http.get(res[app.name]["url"], timeout=5, verify=False)
    assert response.status_code == 200

    _assert_idp_login_success(res[app.name]["url"], endpoint, test_email, test_password)


def _admin_identity_exists(juju, test_email):
    """Check if the admin identity already exists in Kratos."""
    try:
        res = juju.run("kratos/0", "get-identity", {"email": test_email})
        return res.status == "completed"
    except jubilant.TaskError as e:
        logger.info("Error checking admin identity: %s", e)
        return False


def _assert_idp_login_success(app_url: str, endpoint: str, test_email: str, test_password: str):
    """Use playwright to test the OIDC login flow."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(ignore_https_errors=True)
        page = context.new_page()
        return_path = urlparse(url=app_url).path
        page.goto(f"{app_url}/oauth/login/oidc/?next={return_path}/")
        expect(page).not_to_have_title(re.compile("Sign in failed"))
        page.get_by_label("Email").fill(test_email)
        page.get_by_label("Password").fill(test_password)
        page.get_by_role("button", name="Sign in").click()
        expect(page).to_have_url(f"{app_url}/")
        cont = page.content()
        assert "<title>Home | Dashboard</title>" in cont
        cont = page.content()
        # The user is logged in.
        assert test_email in page.content()
        assert "Log Out" in page.content()

# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.

"""Fixtures for the Dashboard charm integration tests."""

import logging
import os.path
import subprocess
from collections.abc import Generator
from typing import cast

import jubilant
import pytest
import requests
from pytest import Config
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from tests.conftest import DASHBOARD_IMAGE_PARAM
from tests.integration.types import App

logger = logging.getLogger(__name__)

# pylint things `juju`` is redefined, but it's a fixture
# pylint: disable=redefined-outer-name

DASHBOARD_APP_NAME = "dashboard"
GATEWAY_APP_NAME = "gateway-api-integrator"
POSTGRESQL_APP_NAME = "postgresql-k8s"
S3_INTEGRATOR_APP_NAME = "s3-integrator"


@pytest.fixture(scope="module", name="dashboard_hostname")
def dashboard_hostname_fixture() -> str:
    """Return the name of the Dashboard hostname used for tests."""
    return "dashboard.internal"


@pytest.fixture(scope="module", name="dashboard_app_image")
def dashboard_app_image_fixture(pytestconfig: Config) -> str:
    """Get value from parameter dashboard-image."""
    dashboard_app_image = pytestconfig.getoption(DASHBOARD_IMAGE_PARAM)
    assert dashboard_app_image, f"{DASHBOARD_IMAGE_PARAM} must be set"
    return dashboard_app_image


@pytest.fixture(scope="module", name="dashboard_charm")
def dashboard_charm_fixture(pytestconfig: Config) -> str:
    """Get value from parameter charm-file."""
    charm = pytestconfig.getoption("--charm-file")
    assert charm, "--charm-file must be set"
    if not os.path.exists(charm):
        logger.info("Using parent directory for charm file")
        charm = os.path.join("..", charm)
    return charm

@pytest.fixture(scope="session")
def juju(request: pytest.FixtureRequest) -> Generator[jubilant.Juju, None, None]:
    """Pytest fixture that wraps :meth:`jubilant.with_model`."""
    use_existing = request.config.getoption("--use-existing", default=False)
    if use_existing:
        juju = jubilant.Juju()
        yield juju
        return

    model = request.config.getoption("--model")
    if model:
        juju = jubilant.Juju(model=model)
        yield juju
        return

    keep_models = cast(bool, request.config.getoption("--keep-models"))
    with jubilant.temp_model(keep=keep_models) as juju:
        juju.wait_timeout = 10 * 60
        yield juju
        return


@pytest.fixture(scope="module", name="gateway_app")
def gateway_app_fixture(
    juju: jubilant.Juju,
) -> App:
    """Deploy gateway-api-integrator."""
    if juju.status().apps.get(GATEWAY_APP_NAME):
        logger.info("%s already deployed", GATEWAY_APP_NAME)
        return App(GATEWAY_APP_NAME)

    juju.deploy(GATEWAY_APP_NAME, base="ubuntu@24.04", channel="latest/edge", trust=True)
    return App(GATEWAY_APP_NAME)


@pytest.fixture(scope="module", name="dashboard_ingress_integration")
def dashboard_ingress_integration_fixture(
    juju: jubilant.Juju,
    gateway_app: App,
    dashboard_app: App,
    dashboard_hostname: str,
):
    """Integrate Dashboard and gateway-api-integrator for ingress integration."""
    juju.config(
        gateway_app.name,
        {"external-hostname": dashboard_hostname, "path-routes": "/", "gateway-class": "cilium"},
    )
    try:
        juju.integrate(
            dashboard_app.name,
            f"{gateway_app.name}:gateway",
        )
    except jubilant.CLIError as e:
        if "already exists" in str(e):
            logger.info("Relation already exists")
        else:
            raise
    juju.wait(
        jubilant.all_active,
        timeout=15 * 60,
    )
    yield dashboard_app
    juju.remove_relation(
        f"{dashboard_app.name}:ingress",
        f"{gateway_app.name}:ingress",
    )


@pytest.fixture(scope="module", name="postgresql_app")
def postgresql_app_fixture(
    juju: jubilant.Juju,
):
    """Deploy and set up postgresql charm needed for the Dashboard charm."""
    if juju.status().apps.get(POSTGRESQL_APP_NAME):
        logger.info("%s already deployed", POSTGRESQL_APP_NAME)
        return App(POSTGRESQL_APP_NAME)

    juju.deploy(
        POSTGRESQL_APP_NAME,
        channel="14/stable",
        base="ubuntu@22.04",
        trust=True,
    )
    return App(POSTGRESQL_APP_NAME)


@pytest.fixture(scope="module", name="dashboard_barebones")
def dashboard_barebones_fixture(
    juju: jubilant.Juju,
    dashboard_charm: str,
    dashboard_app_image: str,
) -> App:
    """Deploy Dashboard app without any relations."""
    status = juju.status()
    if DASHBOARD_APP_NAME in status.apps:
        return App(DASHBOARD_APP_NAME)

    resources = {
        "django-app-image": dashboard_app_image,
    }
    juju.deploy(
        f"./{dashboard_charm}",
        resources=resources,
        config={
            "django-debug": False,
            "django-allowed-hosts": "*",
        },
    )
    return App(DASHBOARD_APP_NAME)


@pytest.fixture(scope="module", name="dashboard_app")
def dashboard_app_fixture(
    juju: jubilant.Juju,
    dashboard_barebones: App,
    postgresql_app: App,
) -> App:
    """Deploy Dashboard app with necessary integrations."""
    try:
        juju.integrate(
            f"{dashboard_barebones.name}:postgresql",
            f"{postgresql_app.name}",
        )
    except jubilant.CLIError as e:
        if "already exists" in str(e):
            logger.info("Relation already exists")
        else:
            raise
    juju.wait(
        lambda status: jubilant.all_active(
            status,
            postgresql_app.name,
            dashboard_barebones.name,
        ),
        timeout=15 * 60,
    )

    return App(dashboard_barebones.name)


@pytest.fixture(scope="module", name="identity_bundle")
def deploy_identity_bundle_fixture(
    juju: jubilant.Juju,
    postgresql_app: App,
):
    """Deploy Canonical identity bundle."""
    if juju.status().apps.get("hydra"):
        logger.info("identity-platform is already deployed")
        return
    juju.deploy("hydra", channel="latest/edge", revision=399, trust=True)
    juju.deploy("kratos", channel="latest/edge", revision=567, trust=True)
    juju.deploy(
        "identity-platform-login-ui-operator", channel="latest/edge", revision=200, trust=True
    )
    juju.deploy("self-signed-certificates", channel="1/stable", revision=317, trust=True)
    juju.deploy("traefik-k8s", "traefik-admin", channel="latest/stable", revision=176, trust=True)
    juju.deploy("traefik-k8s", "traefik-public", channel="latest/edge", revision=270, trust=True)
    # Integrations
    juju.integrate(
        "hydra:hydra-endpoint-info", "identity-platform-login-ui-operator:hydra-endpoint-info"
    )
    juju.integrate("hydra:hydra-endpoint-info", "kratos:hydra-endpoint-info")
    juju.integrate("kratos:kratos-info", "identity-platform-login-ui-operator:kratos-info")
    juju.integrate(
        "hydra:ui-endpoint-info", "identity-platform-login-ui-operator:ui-endpoint-info"
    )
    juju.integrate(
        "kratos:ui-endpoint-info", "identity-platform-login-ui-operator:ui-endpoint-info"
    )
    juju.integrate(f"{postgresql_app.name}:database", "hydra:pg-database")
    juju.integrate(f"{postgresql_app.name}:database", "kratos:pg-database")
    juju.integrate("self-signed-certificates:certificates", "traefik-admin:certificates")
    juju.integrate("self-signed-certificates:certificates", "traefik-public:certificates")
    juju.integrate("traefik-public:traefik-route", "hydra:public-route")
    juju.integrate("traefik-public:traefik-route", "kratos:public-route")
    juju.integrate(
        "traefik-public:traefik-route", "identity-platform-login-ui-operator:public-route"
    )

    juju.config("kratos", {"enforce_mfa": False})
    yield

    _cleanup(juju)


def _cleanup(juju: jubilant.Juju):
    """Remove the test artifacts created during the test."""
    status = juju.status()

    for app in status.apps:
        juju.remove_application(app, force=True, destroy_storage=True)


@pytest.fixture(scope="session")
def browser_context_manager() -> None:
    """
    A session-scoped fixture that installs the Playwright browser.
    This ensures the browser is installed only for oauth test.
    """
    try:
        subprocess.run(
            ["python", "-m", "playwright", "install", "chromium"],
            check=True,
            capture_output=True,
            text=True,
        )
        subprocess.run(
            ["python", "-m", "playwright", "install-deps"],
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as e:
        pytest.fail(f"Failed to install Playwright browser: {e.stderr}")


@pytest.fixture(scope="function", name="http")
def fixture_http_client() -> Generator[requests.Session]:
    """Return the --test-flask-image test parameter."""
    retry_strategy = Retry(
        total=5,
        connect=5,
        read=5,
        other=5,
        backoff_factor=5,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["HEAD", "POST", "GET", "OPTIONS"],
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    with requests.Session() as http:
        http.mount("http://", adapter)
        yield http

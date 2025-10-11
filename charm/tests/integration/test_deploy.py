import pytest
from pytest_operator.plugin import OpsTest


@pytest.mark.abort_on_fail
async def test_build_and_deploy(ops_test: OpsTest):
    """Build the charm and deploy it alongside postgresql-k8s."""

    charm = await ops_test.build_charm(".")
    await ops_test.model.deploy(charm, application_name="canonical-dashboard")
    await ops_test.model.deploy(
        "postgresql-k8s",
        channel="14/stable",
        trust=True,
    )

    # Relate canonical-dashboard with PostgreSQL
    await ops_test.model.add_relation(
        "canonical-dashboard:database", "postgresql-k8s:database"
    )

    await ops_test.model.wait_for_idle(
        apps=["canonical-dashboard", "postgresql-k8s"],
        status="active",
        raise_on_blocked=True,
        timeout=1000,
    )

    assert ops_test.model.applications["canonical-dashboard"].units[0].workload_status == "active"

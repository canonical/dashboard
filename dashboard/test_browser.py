import textwrap

import pytest

from playwright.sync_api import expect

from django.core.management import call_command
from django.urls import reverse
from django.conf import settings

from projects.models import (
    ProjectObjectiveCondition,
    Commitment,
)

from framework.models import Level


# Our tests use 'live_server', so we populate the database every time a test starts.
# See https://pytest-django.readthedocs.io/en/latest/database.html#populate-the-test-database-if-you-use-transactional-or-live-server
#
# We define a custom 'page' fixture that depends on 'live_server' and Playwright's 'page' fixture.
# Since 'live_server' depends on 'transactional_db', we don't need to explicitly mark our tests as
# @pytest.mark.django_db(transaction=True) or have our tests depend on 'transactional_db'.


@pytest.fixture(scope="function")
def django_db_setup(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        call_command("loaddata", "initial_data.yaml")


@pytest.fixture
def page(page, client, live_server):
    """Provides a Playwright `Page` that is logged in to a project page in Django's live server."""

    # Use Django's mock client to simulate a login and capture the session cookie.
    client.login(username="superuser", password="superuser")
    cookie = client.cookies[settings.SESSION_COOKIE_NAME]

    # Inject the session cookie into the browser page.
    page.context.add_cookies([
        {
            "name": settings.SESSION_COOKIE_NAME,
            "value": cookie.value,
            "url": live_server.url,
        }
    ])

    # Navigate the page to the Nuclear project in the live server.
    project_id = 1
    url_end = reverse("projects:project", None, [project_id])
    page.goto(f"{live_server.url}{url_end}")

    yield page


def test_toggling_conditions(page):
    """Check that conditions can be toggled and saved in the database."""

    assert ProjectObjectiveCondition.objects.count() == 1752

    # Toggle project objective condition:
    # Nuclear > Agreeableness > Started > Speaks pleasantly
    assert ProjectObjectiveCondition.objects.get(id=94).status == "DO"
    with page.expect_response("**/action_toggle_condition/94?status=DO&target=done"):
        page.get_by_test_id("toggle_condition_94").uncheck()
    assert ProjectObjectiveCondition.objects.get(id=94).status == ""

    # Toggle project objective condition:
    # Nuclear > Agreeableness > First results > Accepts praise and thanks with grace
    assert ProjectObjectiveCondition.objects.get(id=102).status == ""
    with page.expect_response("**/action_toggle_condition/102?status=&target=done"):
        page.get_by_test_id("toggle_condition_102").check()
    assert ProjectObjectiveCondition.objects.get(id=102).status == "DO"


def test_toggling_commitments(page):
    """Check that commitments can be toggled and saved in the database."""

    # Toggle commitment:
    # Nuclear > Agreeableness > Started > 2022
    assert not Commitment.objects.get(id=705).committed
    with page.expect_response("**/action_toggle_commitment/705"):
        page.get_by_test_id("toggle_commitment_705").check()
    assert Commitment.objects.get(id=705).committed

    # Toggle commitment:
    # Nuclear > Agreeableness > Started > 2025
    assert Commitment.objects.get(id=474).committed
    with page.expect_response("**/action_toggle_commitment/474"):
        page.get_by_test_id("toggle_commitment_474").uncheck()
    assert not Commitment.objects.get(id=474).committed


def test_status(page):
    """Check that objective status is correctly updated based on conditions."""

    # Check that the expected conditions and status are represented on the page.
    # The project objective conditions are under Nuclear > Colourfulness:
    # ------ Started ------
    # 1   Has blue
    # 6   Has green
    # 10  Has red
    # --- First results ---
    # 14  Is striated
    # 18  Is dappled
    # ---------------------
    assert ProjectObjectiveCondition.objects.get(id=1).status == "DO"
    assert ProjectObjectiveCondition.objects.get(id=6).status == "DO"
    assert ProjectObjectiveCondition.objects.get(id=10).status == ""
    assert (
        ProjectObjectiveCondition.objects.get(id=10).projectobjective().status is None
    )
    expect(page.get_by_test_id("projectobjective_status_1")).to_contain_text("")

    # Toggle the remaining condition (Has red) to get to Started.
    with page.expect_response("**/status_projectobjective/1"):
        page.get_by_test_id("toggle_condition_10").check()
    assert ProjectObjectiveCondition.objects.get(
        id=10
    ).projectobjective().status == Level.objects.get(id=1)
    expect(page.get_by_test_id("projectobjective_status_1")).to_contain_text("Started")

    # Toggle two more conditions (Is striated, Is dappled) to get to First results.
    with page.expect_response("**/status_projectobjective/1"):
        page.get_by_test_id("toggle_condition_14").check()
    with page.expect_response("**/status_projectobjective/1"):
        page.get_by_test_id("toggle_condition_18").check()
    assert ProjectObjectiveCondition.objects.get(
        id=18
    ).projectobjective().status == Level.objects.get(id=2)
    expect(page.get_by_test_id("projectobjective_status_1")).to_contain_text(
        "First results"
    )


def csv_from_commitment_table(page):
    """Convert the "Current commitments" table to CSV."""
    row_text = []
    rows = page.query_selector_all("table#commitment-table tr")
    for row in rows[1:]:
        row_values = []
        for cell in row.query_selector_all("td"):
            checkbox = cell.query_selector("input[type='checkbox']")
            if checkbox:
                row_values.append("Y" if checkbox.is_checked() else "N")
            else:
                row_values.append(cell.text_content().strip())
        row_text.append(",".join(row_values))
    return "\n".join(row_text)


@pytest.mark.xfail(
    strict=True, reason="https://github.com/canonical/dashboard/issues/115"
)
def test_commitment_table(page):
    """Check that "Current commitments" updates when commitments, unstarted reason, and conditions are changed."""
    # The table's columns are: objective, level, met (checkbox), unstarted reason.
    # We're using Y/N to represent whether the checkbox is checked.
    assert csv_from_commitment_table(page) == textwrap.dedent("""\
        Agreeableness,Started,Y,
        Colourfulness,Started,N,
        Handling,Started,Y,""")
    # Toggle Colourfulness > First results > 2026.
    with page.expect_response("**/status_projects_commitment/1"):
        page.get_by_test_id("toggle_commitment_3170").check()
    assert csv_from_commitment_table(page) == textwrap.dedent("""\
        Agreeableness,Started,Y,
        Colourfulness,Started,N,
        Colourfulness,First results,N,
        Handling,Started,Y,""")
    # Set Colourfulness unstarted reason to Blocked.
    with page.expect_response("**/status_projects_commitment/1"):
        page.get_by_test_id("projectobjective_ifnotstarted_1").select_option("Blocked")
    # ^ Test fails here because changing the unstarted reason doesn't trigger a table update.
    # Even if it did trigger a table update, the test would fail at the next assert, because
    # the table doesn't currently render the unstarted reason.
    assert csv_from_commitment_table(page) == textwrap.dedent("""\
        Agreeableness,Started,Y,
        Colourfulness,Started,N,Blocked
        Colourfulness,First results,N,Blocked
        Handling,Started,Y,""")
    # Toggle Colourfulness > Started > Has red.
    with page.expect_response("**/status_projects_commitment/1"):
        page.get_by_test_id("toggle_condition_10").check()
    assert csv_from_commitment_table(page) == textwrap.dedent("""\
        Agreeableness,Started,Y,
        Colourfulness,Started,Y,
        Colourfulness,First results,N,
        Handling,Started,Y,""")
    # Toggle Colourfulness > First results > all conditions.
    with page.expect_response("**/status_projects_commitment/1"):
        page.get_by_test_id("toggle_condition_14").check()
    with page.expect_response("**/status_projects_commitment/1"):
        page.get_by_test_id("toggle_condition_18").check()
    assert csv_from_commitment_table(page) == textwrap.dedent("""\
        Agreeableness,Started,Y,
        Colourfulness,Started,Y,
        Colourfulness,First results,Y,
        Handling,Started,Y,""")


def test_last_review(page):
    expect(page.get_by_role("textbox", name="Last review:")).to_have_value("2024-12-16")

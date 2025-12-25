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


@pytest.fixture
def page(django_db_serialized_rollback, browser, live_server, client):
    """Provides a Playwright `Page` that is logged in to a project page in Django's live server."""
    # Need django_db_serialized_rollback because live server and tests run in different threads.
    # See https://pytest-django.readthedocs.io/en/stable/helpers.html#live-server
    # For each test to happen within the scope of a database rollback, our `page` fixture can't
    # depend on Playwright's `page` fixture. It needs to depend on Playwright's `browser` fixture,
    # which is a session fixture.

    # Load sample data and users into the database.
    call_command("loaddata", "initial_data.yaml")

    # Use Django's mock client to simulate a login and capture the session cookie.
    client.login(username="superuser", password="superuser")
    cookie = client.cookies[settings.SESSION_COOKIE_NAME]

    # Create a page in the browser and inject the session cookie.
    browser_context = browser.new_context()
    page = browser_context.new_page()
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
    browser_context.close()


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
                row_values.append("X" if checkbox.is_checked() else "")
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
    # We're using X to represent a checked checkbox.
    assert csv_from_commitment_table(page) == textwrap.dedent("""\
        Agreeableness,Started,X,
        Colourfulness,Started,,
        Handling,Started,X,""")
    # Toggle Colourfulness > First results > 2026.
    with page.expect_response("**/status_projects_commitment/1"):
        page.get_by_test_id("toggle_commitment_3170").check()
    assert csv_from_commitment_table(page) == textwrap.dedent("""\
        Agreeableness,Started,X,
        Colourfulness,Started,,
        Colourfulness,First results,,
        Handling,Started,X,""")
    # Set Colourfulness unstarted reason to Blocked.
    with page.expect_response("**/status_projects_commitment/1"):
        page.get_by_test_id("projectobjective_ifnotstarted_1").select_option("Blocked")
    # ^ Test fails here because changing the unstarted reason doesn't trigger a table update.
    # Even if it did trigger a table update, the test would fail at the next assert, because
    # the table doesn't currently render the unstarted reason.
    assert csv_from_commitment_table(page) == textwrap.dedent("""\
        Agreeableness,Started,X,
        Colourfulness,Started,,Blocked
        Colourfulness,First results,,Blocked
        Handling,Started,X,""")
    # Toggle Colourfulness > Started > Has red.
    with page.expect_response("**/status_projects_commitment/1"):
        page.get_by_test_id("toggle_condition_10").check()
    assert csv_from_commitment_table(page) == textwrap.dedent("""\
        Agreeableness,Started,X,
        Colourfulness,Started,X,
        Colourfulness,First results,,
        Handling,Started,X,""")
    # Toggle Colourfulness > First results > all conditions.
    with page.expect_response("**/status_projects_commitment/1"):
        page.get_by_test_id("toggle_condition_14").check()
    with page.expect_response("**/status_projects_commitment/1"):
        page.get_by_test_id("toggle_condition_18").check()
    assert csv_from_commitment_table(page) == textwrap.dedent("""\
        Agreeableness,Started,X,
        Colourfulness,Started,X,
        Colourfulness,First results,X,
        Handling,Started,X,""")


def test_last_review(page):
    expect(page.get_by_role("textbox", name="Last review:")).to_have_value("2024-12-16")

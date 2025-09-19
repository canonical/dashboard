import time

import pytest

from playwright.sync_api import Page, expect

from django.core.management import call_command
from django.urls import reverse
from django.contrib.auth.models import User
from django.test.client import Client
from django.conf import settings

from projects.models import (
    Project,
    ProjectObjective,
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
    # check ProjectObjectiveCondition
    # check that the expected conditions are represented on the page
    assert ProjectObjectiveCondition.objects.count() == 697
    assert ProjectObjectiveCondition.objects.get(id=94).done == True
    assert ProjectObjectiveCondition.objects.get(id=102).done == False

    # after toggling, the new conditions should be saved in the database
    page.get_by_test_id("toggle_condition_94").uncheck()
    page.get_by_test_id("toggle_condition_102").check()
    time.sleep(5)  # Temporary workaround. Find a better solution.

    assert ProjectObjectiveCondition.objects.get(id=94).done == False
    assert ProjectObjectiveCondition.objects.get(id=102).done == True

    # check Commitment
    # check that the expected commitments are represented on the page
    assert Commitment.objects.get(id=705).committed == False
    assert Commitment.objects.get(id=474).committed == True

    page.get_by_test_id("toggle_commitment_705").check()
    page.get_by_test_id("toggle_commitment_474").uncheck()
    time.sleep(5)  # Temporary workaround. Find a better solution.

    assert Commitment.objects.get(id=705).committed == True
    assert Commitment.objects.get(id=474).committed == False

    # check Status
    # check that the expected conditions and status are represented on the page
    assert ProjectObjectiveCondition.objects.get(id=1).done == True
    assert ProjectObjectiveCondition.objects.get(id=6).done == True
    assert ProjectObjectiveCondition.objects.get(id=10).done == False
    assert ProjectObjectiveCondition.objects.get(id=10).not_applicable == False
    assert (
        ProjectObjectiveCondition.objects.get(id=10).projectobjective().status() == None
    )
    expect(page.get_by_test_id("projectobjective_status_1")).to_contain_text("")

    # check the remaining box to get to Started
    page.get_by_test_id("toggle_condition_10").check()
    time.sleep(5)  # Temporary workaround. Find a better solution.
    assert ProjectObjectiveCondition.objects.get(
        id=10
    ).projectobjective().status() == Level.objects.get(id=1)
    expect(page.get_by_test_id("projectobjective_status_1")).to_contain_text("Started")

    # check one more to get to First results
    page.get_by_test_id("toggle_condition_14").check()
    time.sleep(5)  # Temporary workaround. Find a better solution.
    assert ProjectObjectiveCondition.objects.get(
        id=14
    ).projectobjective().status() == Level.objects.get(id=1)
    expect(page.get_by_test_id("projectobjective_status_1")).to_contain_text("Started")

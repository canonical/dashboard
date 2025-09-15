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

@pytest.fixture(scope="session")
def django_db_setup(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        call_command("loaddata", "initial_data.yaml")

def reverse_url(
    live_server, viewname, urlconf=None, args=None, kwargs=None, current_app=None
):
    end = reverse(viewname, urlconf, args, kwargs, current_app)
    return f"{live_server.url}{end}"

@pytest.fixture
def page(page, live_server):

    c = Client()
    c.login(username="superuser", password="superuser")
    session_cookie = c.cookies[settings.SESSION_COOKIE_NAME]
    page.context.add_cookies([{
        "name": settings.SESSION_COOKIE_NAME,
        "value": session_cookie.value,
        "url": live_server.url,
    }])
    return page


def test_toggling_conditions(live_server, page):

    url = reverse_url(live_server, viewname="projects:project", args=[1])
    page.goto(url)

    # check ProjectObjectiveCondition
    # check that the expected conditions are represented on the page
    assert ProjectObjectiveCondition.objects.count() == 697
    assert ProjectObjectiveCondition.objects.get(id=94).done == True
    assert ProjectObjectiveCondition.objects.get(id=102).done == False

    # after toggling, the new conditions should be saved in the database
    page.get_by_test_id("toggle_condition_94").uncheck()
    page.get_by_test_id("toggle_condition_102").check()
    time.sleep(1)  # Temporary workaround. Find a better solution.

    assert ProjectObjectiveCondition.objects.get(id=94).done == False
    assert ProjectObjectiveCondition.objects.get(id=102).done == True

    # check Commitment
    # check that the expected commitments are represented on the page
    assert Commitment.objects.get(id=705).committed == False
    assert Commitment.objects.get(id=474).committed == True

    page.get_by_test_id("toggle_commitment_705").check()
    page.get_by_test_id("toggle_commitment_474").uncheck()
    time.sleep(1)  # Temporary workaround. Find a better solution.

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
    time.sleep(1)  # Temporary workaround. Find a better solution.
    assert ProjectObjectiveCondition.objects.get(
        id=10
    ).projectobjective().status() == Level.objects.get(id=1)
    expect(page.get_by_test_id("projectobjective_status_1")).to_contain_text("Started")

    # check one more to get to First results
    page.get_by_test_id("toggle_condition_14").check()
    time.sleep(1)  # Temporary workaround. Find a better solution.
    assert ProjectObjectiveCondition.objects.get(
        id=14
    ).projectobjective().status() == Level.objects.get(id=1)
    expect(page.get_by_test_id("projectobjective_status_1")).to_contain_text("Started")

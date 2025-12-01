import datetime
import pytest

from django.urls import reverse
from django.contrib.messages import get_messages

from framework.models import WorkCycle, ObjectiveGroup, Objective, Level
from projects.models import Project, QI, ProjectObjective


@pytest.fixture
def work_cycle():
    return WorkCycle.objects.create(
        name="test_work_cycle", timestamp=datetime.date.today()
    )


@pytest.fixture
def objective_group():
    return ObjectiveGroup.objects.create(name="test_objective_group")


@pytest.fixture
def objective(objective_group):
    return Objective.objects.create(
        name="test_objective", group=objective_group, weight=5
    )


@pytest.fixture
def level():
    return Level.objects.create(name="test_level", value=3)


@pytest.fixture
def project(objective):
    # Creating a project will automatically create QI objects for all workcycles
    return Project.objects.create(
        name="test_project", owner="test_owner", driver="test_driver"
    )


@pytest.mark.django_db
def test_admin_apply_qis(client, work_cycle, project, objective, level):
    """Test that admin_apply_qis copies current QI values to workcycle QIs."""

    # Set up: Create a ProjectObjective with a status that has a value,
    # by overriding the ProjectObjective's level calculation
    po = ProjectObjective.objects.get(project=project, objective=objective)
    po.achieved_level = level
    po.save()

    # The project's quality_indicator should now have a value
    # quality_indicator = sum(po.status.value * po.objective.weight)
    # For this test, let's assume it calculates to some value
    initial_qi_value = project.quality_indicator
    assert initial_qi_value != 0

    # Get the QI object for this workcycle and project
    qi = QI.objects.get(workcycle=work_cycle, project=project)

    # Initially, the QI value should be 0 (default)
    assert qi.value == 0

    # Call the admin_apply_qis view
    url = reverse("framework:admin_apply_qis", args=[work_cycle.id])
    response = client.get(url)

    # Check that it redirects to the admin change page
    assert response.status_code == 302
    expected_redirect = reverse(
        "admin:framework_workcycle_change", args=[work_cycle.id]
    )
    assert response.url == expected_redirect

    # Refresh the QI from the database
    qi.refresh_from_db()

    # The QI value should now match the project's quality_indicator
    assert qi.value == initial_qi_value


@pytest.mark.django_db
def test_admin_apply_qis_with_multiple_projects(client, work_cycle, objective, level):
    """Test that admin_apply_qis updates QIs for multiple projects."""

    # Create multiple projects
    project1 = Project.objects.create(
        name="project_1", owner="owner_1", driver="driver_1"
    )
    po1 = ProjectObjective.objects.get(project=project1, objective=objective)
    po1.achieved_level = level
    po1.save()
    assert project1.quality_indicator != 0
    project2 = Project.objects.create(
        name="project_2", owner="owner_2", driver="driver_2"
    )
    po2 = ProjectObjective.objects.get(project=project2, objective=objective)
    po2.achieved_level = level
    po2.save()
    assert project2.quality_indicator != 0

    # Get QI objects for both projects
    qi1 = QI.objects.get(workcycle=work_cycle, project=project1)
    qi2 = QI.objects.get(workcycle=work_cycle, project=project2)

    # Verify initial values are 0
    assert qi1.value == 0
    assert qi2.value == 0

    # Call the admin_apply_qis view
    url = reverse("framework:admin_apply_qis", args=[work_cycle.id])
    client.get(url)

    # Refresh QIs from database
    qi1.refresh_from_db()
    qi2.refresh_from_db()

    # Both QI values should now match their respective project quality indicators
    assert qi1.value == project1.quality_indicator
    assert qi2.value == project2.quality_indicator


@pytest.mark.django_db
def test_admin_apply_qis_shows_message(client, work_cycle, project):
    """Test that admin_apply_qis displays an info message."""

    url = reverse("framework:admin_apply_qis", args=[work_cycle.id])
    response = client.get(url, follow=True)

    # Check that the message was added
    messages = list(get_messages(response.wsgi_request))
    assert len(messages) == 1
    assert str(messages[0]) == "Copied current QI values."


@pytest.mark.django_db
def test_admin_apply_qis_with_no_projects(client, work_cycle):
    """Test that admin_apply_qis works even when no projects exist."""

    # Call the view with no projects
    url = reverse("framework:admin_apply_qis", args=[work_cycle.id])
    response = client.get(url)

    # Should still redirect successfully
    assert response.status_code == 302
    expected_redirect = reverse(
        "admin:framework_workcycle_change", args=[work_cycle.id]
    )
    assert response.url == expected_redirect

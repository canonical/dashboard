import pytest
from urllib.parse import parse_qs, urlparse

from django.urls import reverse
from django.contrib.auth.models import Permission, User

from framework.models import (
    Condition,
    Level,
    Objective,
    ObjectiveGroup,
    Reason,
    WorkCycle,
)
from projects.models import (
    Commitment,
    Project,
    ProjectObjective,
    ProjectObjectiveCondition,
)


def test_toggle_condition_url_patterns():
    url = reverse("projects:action_toggle_condition", args=[1])
    assert url == "/action_toggle_condition/1"


@pytest.fixture
def user_without_permissions(client):
    user = User.objects.create_user(username="no_perm", password="password")
    client.login(username="no_perm", password="password")
    return user


@pytest.fixture
def user_can_change_commitment(client):
    user = User.objects.create_user(username="change_commitment", password="password")
    permission = Permission.objects.get(
        codename="change_commitment",
        content_type__app_label="projects",
    )
    user.user_permissions.add(permission)
    client.login(username="change_commitment", password="password")
    return user


@pytest.fixture
def user_can_change_projectobjectivecondition(client):
    user = User.objects.create_user(
        username="change_projectobjectivecondition", password="password"
    )
    permission = Permission.objects.get(
        codename="change_projectobjectivecondition",
        content_type__app_label="projects",
    )
    user.user_permissions.add(permission)
    client.login(username="change_projectobjectivecondition", password="password")
    return user


@pytest.fixture
def user_can_change_projectobjective(client):
    user = User.objects.create_user(
        username="change_projectobjective", password="password"
    )
    permission = Permission.objects.get(
        codename="change_projectobjective",
        content_type__app_label="projects",
    )
    user.user_permissions.add(permission)
    client.login(username="change_projectobjective", password="password")
    return user


@pytest.fixture
def objective_group():
    return ObjectiveGroup.objects.create(name="group")


@pytest.fixture
def objective(objective_group):
    return Objective.objects.create(name="objective", group=objective_group, weight=1)


@pytest.fixture
def level():
    return Level.objects.create(name="level", value=1)


@pytest.fixture
def work_cycle():
    return WorkCycle.objects.create(name="wc", timestamp="2026-01-01", is_current=True)


@pytest.fixture
def project(objective, level, work_cycle):
    return Project.objects.create(name="project")


@pytest.fixture
def condition(objective, level):
    return Condition.objects.create(name="condition", objective=objective, level=level)


@pytest.fixture
def project_objective(project, objective):
    return ProjectObjective.objects.get(project=project, objective=objective)


@pytest.fixture
def project_objective_condition(project, objective, condition):
    return ProjectObjectiveCondition.objects.get(
        project=project,
        objective=objective,
        condition=condition,
    )


@pytest.fixture
def commitment(project, objective, level, work_cycle):
    return Commitment.objects.get(
        project=project,
        objective=objective,
        level=level,
        work_cycle=work_cycle,
    )


@pytest.fixture
def reason():
    return Reason.objects.create(name="not-started", value=1)


@pytest.mark.django_db
def test_action_toggle_commitment_denies_user_without_permission(
    client, user_without_permissions, commitment
):
    url = reverse("projects:action_toggle_commitment", args=[commitment.id])
    response = client.put(url)

    assert response.status_code == 302
    expected_redirect = f"{reverse('login')}?next={url}"
    assert response.url == expected_redirect


@pytest.mark.django_db
def test_action_toggle_condition_denies_user_without_permission(
    client, user_without_permissions, project_objective_condition
):
    url = (
        reverse(
            "projects:action_toggle_condition",
            args=[project_objective_condition.id],
        )
        + "?status=&target=done"
    )
    response = client.put(url)

    assert response.status_code == 302
    parsed = urlparse(response.url)
    assert parsed.path == reverse("login")
    assert parse_qs(parsed.query)["next"][0] == url


@pytest.mark.django_db
def test_action_select_reason_denies_user_without_permission(
    client, user_without_permissions, project_objective, reason
):
    url = reverse("projects:action_select_reason", args=[project_objective.id])
    response = client.generic(
        "PUT",
        url,
        data=f"ifnotstarted={reason.id}",
        content_type="application/x-www-form-urlencoded",
    )

    assert response.status_code == 302
    expected_redirect = f"{reverse('login')}?next={url}"
    assert response.url == expected_redirect


@pytest.mark.django_db
def test_action_toggle_commitment_rejects_non_put_method(
    client, user_can_change_commitment, commitment
):
    url = reverse("projects:action_toggle_commitment", args=[commitment.id])
    response = client.get(url)

    assert response.status_code == 405


@pytest.mark.django_db
def test_action_toggle_commitment_allows_authorized_put_and_updates_commitment(
    client, user_can_change_commitment, commitment
):
    assert commitment.committed is False

    url = reverse("projects:action_toggle_commitment", args=[commitment.id])
    response = client.put(url)

    commitment.refresh_from_db()
    assert response.status_code == 200
    assert commitment.committed is True
    assert response["HX-Trigger-After-Swap"] == "updateCommitment"


@pytest.mark.django_db
def test_action_toggle_condition_rejects_non_put_method(
    client, user_can_change_projectobjectivecondition, project_objective_condition
):
    url = (
        reverse(
            "projects:action_toggle_condition",
            args=[project_objective_condition.id],
        )
        + "?status=&target=done"
    )
    response = client.get(url)

    assert response.status_code == 405


@pytest.mark.django_db
def test_action_toggle_condition_allows_authorized_put_and_updates_status(
    client, user_can_change_projectobjectivecondition, project_objective_condition
):
    assert project_objective_condition.status == ""

    url = (
        reverse(
            "projects:action_toggle_condition",
            args=[project_objective_condition.id],
        )
        + "?status=&target=done"
    )
    response = client.put(url)

    project_objective_condition.refresh_from_db()
    assert response.status_code == 200
    assert project_objective_condition.status == "DO"
    assert "HX-Trigger-After-Swap" in response


@pytest.mark.django_db
def test_action_select_reason_rejects_non_put_method(
    client, user_can_change_projectobjective, project_objective
):
    url = reverse("projects:action_select_reason", args=[project_objective.id])
    response = client.get(url)

    assert response.status_code == 405


@pytest.mark.django_db
def test_action_select_reason_allows_authorized_put_and_sets_reason(
    client, user_can_change_projectobjective, project_objective, reason
):
    assert project_objective.unstarted_reason is None

    url = reverse("projects:action_select_reason", args=[project_objective.id])
    response = client.generic(
        "PUT",
        url,
        data=f"ifnotstarted={reason.id}",
        content_type="application/x-www-form-urlencoded",
    )

    project_objective.refresh_from_db()
    assert response.status_code == 200
    assert project_objective.unstarted_reason_id == reason.id

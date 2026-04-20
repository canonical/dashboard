import pytest
from urllib.parse import parse_qs, urlparse

from django.test import override_settings
from django.urls import reverse
from django.contrib.auth.models import Permission, User

from framework.models import Condition, Level, Objective, ObjectiveGroup, Reason, WorkCycle
from projects.models import Commitment, Project, ProjectObjective, ProjectObjectiveCondition

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
    QI,
)


def test_toggle_condition_url_patterns():
    url = reverse("projects:action_toggle_condition", args=[1])
    assert url == "/action_toggle_condition/1"


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
<<<<<<< HEAD
<<<<<<< HEAD
=======
>>>>>>> 7781581 (Added a permissions constraint for project_basic_form_save)
def test_project_basic_form_save_denies_unauthenticated_user(client, project):
    original_owner = project.owner
    url = reverse("projects:project_basic_form_save", args=[project.id])
    response = client.post(
        url,
        data={
            "name": project.name,
            "url": project.url,
            "group": "",
            "owner": "changed owner",
            "driver": project.driver or "",
            "agreement_status": "",
            "last_review": "",
            "last_review_status": "",
        },
    )

    project.refresh_from_db()
    assert response.status_code == 302
    assert response.url == f"{reverse('login')}?next={url}"
    assert project.owner == original_owner


@pytest.mark.django_db
def test_project_basic_form_save_denies_user_without_permission(
    client, user_without_permissions, project
):
    original_owner = project.owner
    url = reverse("projects:project_basic_form_save", args=[project.id])
    response = client.post(
        url,
        data={
            "name": project.name,
            "url": project.url,
            "group": "",
            "owner": "changed owner",
            "driver": project.driver or "",
            "agreement_status": "",
            "last_review": "",
            "last_review_status": "",
        },
    )

    project.refresh_from_db()
    assert response.status_code == 302
    assert response.url == f"{reverse('login')}?next={url}"
    assert project.owner == original_owner


@pytest.mark.django_db
<<<<<<< HEAD
def test_project_basic_form_save_allows_user_with_permission(
    client, user_can_change_project, project
):
=======
def test_project_basic_form_save_allows_user_with_permission(client, user_can_change_project, project):
>>>>>>> 7781581 (Added a permissions constraint for project_basic_form_save)
    url = reverse("projects:project_basic_form_save", args=[project.id])
    response = client.post(
        url,
        data={
            "name": project.name,
            "url": project.url,
            "group": "",
            "owner": "changed owner",
            "driver": project.driver or "",
            "agreement_status": "",
            "last_review": "",
            "last_review_status": "",
        },
    )

    project.refresh_from_db()
    assert response.status_code == 200
    assert project.owner == "changed owner"


@pytest.mark.django_db
<<<<<<< HEAD
=======
>>>>>>> 3a8a10d (Added a series of tests for view functions)
=======
>>>>>>> 7781581 (Added a permissions constraint for project_basic_form_save)
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
<<<<<<< HEAD
            "projects:action_toggle_condition",
            args=[project_objective_condition.id],
=======
        "projects:action_toggle_condition",
        args=[project_objective_condition.id],
>>>>>>> 3a8a10d (Added a series of tests for view functions)
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
<<<<<<< HEAD
            "projects:action_toggle_condition",
            args=[project_objective_condition.id],
=======
        "projects:action_toggle_condition",
        args=[project_objective_condition.id],
>>>>>>> 3a8a10d (Added a series of tests for view functions)
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
<<<<<<< HEAD
            "projects:action_toggle_condition",
            args=[project_objective_condition.id],
=======
        "projects:action_toggle_condition",
        args=[project_objective_condition.id],
>>>>>>> 3a8a10d (Added a series of tests for view functions)
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
<<<<<<< HEAD


@pytest.mark.django_db
def test_project_list_renders_qi_history_current_qi_and_levels(
    client, user_without_permissions, objective, project, project_objective, work_cycle
):
    second_work_cycle = WorkCycle.objects.create(
        name="wc-2", timestamp="2026-02-01", is_current=False
    )
    QI.objects.update_or_create(
        project=project,
        workcycle=work_cycle,
        defaults={"value": 3},
    )
    QI.objects.update_or_create(
        project=project,
        workcycle=second_work_cycle,
        defaults={"value": 5},
    )

    level_for_display = Level.objects.create(name="LEVEL-ASSERT-ONLY", value=7)
    ProjectObjective.objects.filter(id=project_objective.id).update(
        level_achieved=level_for_display
    )

    response = client.get(reverse("projects:project_list"))
    content = response.content.decode()

    assert response.status_code == 200
    assert "<td>3</td>" in content
    assert "<td>5</td>" in content
    assert ">7</a></td>" in content
    assert "LEVEL-ASSERT-ONLY" in content


# Check that the project list and project detail pages are correctly public/private,
# depending on whether OIDC is configured.


@pytest.mark.django_db
@override_settings(FORCE_LOGIN=False)
def test_no_login_project_list(client):
    url = reverse("projects:project_list")
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
@override_settings(FORCE_LOGIN=True)
def test_force_login_project_list(client):
    url = reverse("projects:project_list")
    response = client.get(url)
    assert response.status_code == 302
    expected_redirect = f"{reverse('login')}?next={url}"
    assert response.url == expected_redirect


@pytest.mark.django_db
@override_settings(FORCE_LOGIN=True)
def test_force_login_project_list_with_user(client, user_without_permissions):
    url = reverse("projects:project_list")
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
@override_settings(FORCE_LOGIN=False)
def test_no_login_project_detail(client, project):
    url = reverse("projects:project", kwargs={"id": project.id})
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
@override_settings(FORCE_LOGIN=True)
def test_force_login_project_detail(client, project):
    url = reverse("projects:project", kwargs={"id": project.id})
    response = client.get(url)
    assert response.status_code == 302
    expected_redirect = f"{reverse('login')}?next={url}"
    assert response.url == expected_redirect


@pytest.mark.django_db
@override_settings(FORCE_LOGIN=True)
def test_force_login_project_detail_with_user(client, user_without_permissions, project):
    url = reverse("projects:project", kwargs={"id": project.id})
    response = client.get(url)
    assert response.status_code == 200
=======
>>>>>>> 3a8a10d (Added a series of tests for view functions)

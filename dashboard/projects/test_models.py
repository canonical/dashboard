import pytest

from projects.models import *


@pytest.mark.django_db
def test_admin_recalculate_all_levels(client):
    project = Project.objects.create(name="project")
    level1 = Level.objects.create(name="level_1", value=1)
    level2 = Level.objects.create(name="level_2", value=2)
    objective1 = Objective.objects.create(name="objective_1", weight=1)
    condition1 = Condition.objects.create(
        name="condition_1", level=level1, objective=objective1
    )
    condition2 = Condition.objects.create(
        name="condition_2", level=level2, objective=objective1
    )

    po = ProjectObjective.objects.get(project=project, objective=objective1)
    assert po.level_achieved == None

    # the objective meets level 1, but save() hasn't yet been called
    # so level_achieved is out of date
    ProjectObjectiveCondition.objects.filter(
        project=project,
        objective=objective1,
        condition=condition1,
    ).update(status="DO")

    assert po.level_achieved == None

    # Call the admin_apply_qis view
    url = reverse("projects:admin_recalculate_all_levels")
    response = client.get(url)

    # Check that it redirects to the admin change page
    assert response.status_code == 302
    expected_response = reverse("admin:index")
    assert response.url == expected_response

    # # Refresh the level from the database
    po.refresh_from_db()

    # The status should now be level1
    assert po.level_achieved == level1

    # the objective meets level 2
    ProjectObjectiveCondition.objects.filter(
        project=project,
        objective=objective1,
        condition=condition2,
    ).update(status="DO")

    url = reverse("projects:admin_recalculate_all_levels")
    response = client.get(url)
    po.refresh_from_db()
    assert po.level_achieved == level2


@pytest.mark.django_db
def test_project_objective_achieved_level():
    project = Project.objects.create(name="project")
    level1 = Level.objects.create(name="level_1", value=1)
    level2 = Level.objects.create(name="level_2", value=2)
    level3 = Level.objects.create(name="level_3", value=3)
    objective1 = Objective.objects.create(name="objective_1", weight=1)
    condition1 = Condition.objects.create(
        name="condition_1", level=level1, objective=objective1
    )
    condition2 = Condition.objects.create(
        name="condition_2", level=level1, objective=objective1
    )
    ProjectObjectiveCondition.objects.filter(
        project=project,
        objective=objective1,
        condition=condition1,
    ).update(status="DO")

    ProjectObjectiveCondition.objects.filter(
        project=project,
        objective=objective1,
        condition=condition2,
    ).update(status="CA")

    po = ProjectObjective.objects.get(project=project, objective=objective1)
    assert po.achieved_level == None

    ProjectObjectiveCondition.objects.filter(
       project=project,
       objective=objective1,
       condition=condition2,
    ).update(status="NA")

    po = ProjectObjective.objects.get(project=project, objective=objective1)
    assert po.achieved_level == level1

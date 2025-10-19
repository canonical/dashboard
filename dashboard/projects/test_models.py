import pytest

from projects.models import *


@pytest.mark.django_db
def test_expectations_are_confirmed():
    project = Project.objects.create(name="project")
    level1 = Level.objects.create(name="level_1", value=1)
    level2 = Level.objects.create(name="level_2", value=2)
    level3 = Level.objects.create(name="level_3", value=3)
    objective1 = Objective.objects.create(name="objective_1", weight=1)
    condition1 = Condition.objects.create(
        name="condition_1", level=level1, objective=objective1
    )
    condition2 = Condition.objects.create(
        name="condition_2", level=level3, objective=objective1
    )

    # the objective meets level 1
    ProjectObjectiveCondition.objects.filter(
        project=project,
        objective=objective1,
        condition=condition1,
    ).update(status="DO")
    assert (
        ProjectObjective.objects.get(project=project, objective=objective1).status()
        == level1
    )

    # the objective meets level 3
    ProjectObjectiveCondition.objects.filter(
        project=project,
        objective=objective1,
        condition=condition2,
    ).update(status="DO")
    assert (
        ProjectObjective.objects.get(project=project, objective=objective1).status()
        == level3
    )

import datetime
from pytest_django.asserts import assertQuerySetEqual

import pytest

from framework.models import WorkCycle, ObjectiveGroup, Objective, Condition, Level
from projects.models import (
    Project,
    ProjectObjective,
    ProjectObjectiveCondition,
    LevelCommitment,
)


@pytest.fixture
def objective_group():
    return ObjectiveGroup.objects.create(name="test_objective_group")


@pytest.fixture
def work_cycle():
    return WorkCycle.objects.create(name="test_work_cycle_1", timestamp=datetime.date.today())


@pytest.fixture
def level():
    return Level.objects.create(name="test_level", value=1)


@pytest.fixture
def project():
    return Project.objects.create(
        name="test_project", owner="test_owner", driver="test_driver"
    )


@pytest.fixture
def objective(objective_group):
    return Objective.objects.get_or_create(
        name="test_objective", group=objective_group, weight=1
    )[0]


@pytest.fixture
def condition(level, objective):
    return Condition.objects.create(
        name="test_condition", level=level, objective=objective
    )


@pytest.fixture
def project_objective(project, objective):
    return ProjectObjective.objects.get_or_create(project=project, objective=objective)[
        0
    ]


@pytest.mark.django_db
def test_expectations_are_confirmed(project, objective):
    assert Project.objects.count() == 1
    assert Objective.objects.count() == 1
    assert ProjectObjective.objects.count() == 1


@pytest.mark.django_db
def test_new_condition_is_propagated_to_projectobjectives(project, objective, level):

    assert ProjectObjective.objects.count() == 1
    assert ProjectObjectiveCondition.objects.count() == 0
    condition = Condition.objects.create(
        name="test_condition", objective=objective, level=level
    )

    # there should be a new ProjectObjectiveCondition on project_objective, with the new Condition
    projectobjective = ProjectObjective.objects.get(
        objective=objective, project=project
    )
    assert ProjectObjectiveCondition.objects.filter(
        objective=objective, project=project, condition=condition
    ).exists()
    assert ProjectObjectiveCondition.objects.count() == 1


@pytest.mark.django_db
def test_new_objective_is_propagated_to_projects(
    objective, project, objective_group, condition
):

    assert project.projectobjective_set.count() == 1
    assert project.projectobjective_set.count() == 1
    objective = Objective.objects.create(
        name="test_objective_2", group=objective_group, weight=1
    )

    # there should be a new ProjectObjective on project, for the new Objective
    assert project.projectobjective_set.count() == 2
    assert project.projectobjective_set.filter(objective=objective).exists()


@pytest.mark.django_db
def test_new_project_acquires_projectiveconditions(
    objective, objective_group, condition
):

    project = Project.objects.create(
        name="test_project", owner="test_owner", driver="test_driver"
    )
    assert project.projectobjectivecondition_set.count() == 1
    assert project.projectobjectivecondition_set.all()[0].objective == objective


@pytest.mark.django_db
def test_new_project_acquires_levelcommitments(
    objective, objective_group, condition, work_cycle
):

    project = Project.objects.create(
        name="test_project", owner="test_owner", driver="test_driver"
    )
    assert project.pk == 1
    assert project.levelcommitment_set.count() == 1
    assert project.levelcommitment_set.all()[0].objective == objective


@pytest.mark.django_db
def test_workcycle_is_propagated_to_levelcommitments(
    work_cycle, condition, project_objective
):

    assert work_cycle.levelcommitment_set.count() == 1
    work_cycle = WorkCycle.objects.create(name="test_work_cycle_2", timestamp=datetime.date.today())

    # there should be a new LevelCommitment
    assert work_cycle.levelcommitment_set.count() == 1
    assert LevelCommitment.objects.count() == 2
    assert work_cycle.levelcommitment_set.filter(work_cycle=work_cycle).exists()


@pytest.mark.django_db
def test_new_objective_means_new_levelcommitments(
    project, project_objective, objective_group, condition, work_cycle
    ):
    assert project.levelcommitment_set.count() == 1
    objective = Objective.objects.create(
        name="test_objective_2", group=objective_group, weight=1
    )
    assert project.levelcommitment_set.count() == 2

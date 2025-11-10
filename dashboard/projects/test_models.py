import pytest
from django.urls import reverse

from framework.models import ObjectiveGroup, Objective, Level, Condition
from projects.models import (
    Project,
    ProjectObjective,
    ProjectObjectiveCondition,
)


@pytest.fixture
def objective_group():
    return ObjectiveGroup.objects.create(name="test_objective_group")


@pytest.fixture
def project():
    return Project.objects.create(
        name="test_project", owner="test_owner", driver="test_driver"
    )


@pytest.fixture
def objective(objective_group):
    return Objective.objects.create(
        name="test_objective", group=objective_group, weight=1
    )


@pytest.fixture
def level1():
    return Level.objects.create(name="level_1", value=1)


@pytest.fixture
def level2():
    return Level.objects.create(name="level_2", value=2)


@pytest.fixture
def level3():
    return Level.objects.create(name="level_3", value=3)


@pytest.fixture
def condition1(level1, objective):
    return Condition.objects.create(
        name="condition_1", level=level1, objective=objective
    )


@pytest.fixture
def condition2(level2, objective):
    return Condition.objects.create(
        name="condition_2", level=level2, objective=objective
    )


@pytest.mark.django_db
def test_admin_recalculate_all_levels(client, project, objective, level1, level2, condition1, condition2):
    """Test that admin_recalculate_all_levels recalculates ProjectObjective.level_achieved."""
    
    po = ProjectObjective.objects.get(project=project, objective=objective)
    assert po.level_achieved == None

    # the objective meets level 1, but save() hasn't yet been called
    # so level_achieved is out of date
    ProjectObjectiveCondition.objects.filter(
        project=project,
        objective=objective,
        condition=condition1,
    ).update(status="DO")

    assert po.level_achieved == None

    # Call the admin_recalculate_all_levels view
    url = reverse("projects:admin_recalculate_all_levels")
    response = client.get(url)

    # Check that it redirects to the admin change page
    assert response.status_code == 302
    expected_response = reverse("admin:index")
    assert response.url == expected_response

    # Refresh the level from the database
    po.refresh_from_db()

    # The status should now be level1
    assert po.level_achieved == level1

    # the objective meets level 2
    ProjectObjectiveCondition.objects.filter(
        project=project,
        objective=objective,
        condition=condition2,
    ).update(status="DO")

    url = reverse("projects:admin_recalculate_all_levels")
    response = client.get(url)
    po.refresh_from_db()
    assert po.level_achieved == level2


@pytest.mark.django_db
def test_project_objective_achieved_level(project, objective, level1):
    """Test that ProjectObjective.achieved_level is calculated correctly."""
    
    # Create two conditions at the same level
    condition1 = Condition.objects.create(
        name="condition_1", level=level1, objective=objective
    )
    condition2 = Condition.objects.create(
        name="condition_2", level=level1, objective=objective
    )
    
    # Mark one as done, one as candidate
    ProjectObjectiveCondition.objects.filter(
        project=project,
        objective=objective,
        condition=condition1,
    ).update(status="DO")

    ProjectObjectiveCondition.objects.filter(
        project=project,
        objective=objective,
        condition=condition2,
    ).update(status="CA")

    po = ProjectObjective.objects.get(project=project, objective=objective)
    assert po.achieved_level == None

    # Mark the second one as not applicable
    ProjectObjectiveCondition.objects.filter(
       project=project,
       objective=objective,
       condition=condition2,
    ).update(status="NA")

    po = ProjectObjective.objects.get(project=project, objective=objective)
    assert po.achieved_level == level1


@pytest.mark.django_db
def test_quality_indicator_with_no_objectives():
    """Test QI is 0 when project has no objectives."""
    project = Project.objects.create(name="empty_project")
    assert project.quality_indicator() == 0


@pytest.mark.django_db
def test_quality_indicator_with_no_levels_achieved(project, objective):
    """Test QI is 0 when objectives have no levels achieved."""
    po = ProjectObjective.objects.get(project=project, objective=objective)
    assert po.level_achieved is None
    assert project.quality_indicator() == 0


@pytest.mark.django_db
def test_quality_indicator_single_objective(project, objective, level1):
    """Test QI calculation with one objective at one level."""
    # objective.weight = 1 (from fixture)
    # level1.value = 1 (from fixture)
    # Expected: 1 * 1 = 1
    
    ProjectObjective.objects.filter(
        project=project, objective=objective
    ).update(level_achieved=level1)
    
    assert project.quality_indicator() == 1


@pytest.mark.django_db
def test_quality_indicator_multiple_objectives(project, objective_group):
    """Test QI sums across multiple objectives."""
    obj1 = Objective.objects.create(name="obj1", group=objective_group, weight=10)
    obj2 = Objective.objects.create(name="obj2", group=objective_group, weight=5)
    
    level_a = Level.objects.create(name="level_a", value=2)
    level_b = Level.objects.create(name="level_b", value=4)
    
    ProjectObjective.objects.filter(
        project=project, objective=obj1
    ).update(level_achieved=level_a)
    
    ProjectObjective.objects.filter(
        project=project, objective=obj2
    ).update(level_achieved=level_b)
    
    # Expected: (10 * 2) + (5 * 4) = 20 + 20 = 40
    assert project.quality_indicator() == 40


@pytest.mark.django_db
def test_quality_indicator_mixed_achieved_and_none(project, objective_group):
    """Test QI ignores objectives with no level_achieved."""
    obj1 = Objective.objects.create(name="obj1", group=objective_group, weight=10)
    obj2 = Objective.objects.create(name="obj2", group=objective_group, weight=5)
    
    level_a = Level.objects.create(name="level_a", value=3)
    
    ProjectObjective.objects.filter(
        project=project, objective=obj1
    ).update(level_achieved=level_a)
    
    po2 = ProjectObjective.objects.get(project=project, objective=obj2)
    assert po2.level_achieved is None
    
    # Expected: only obj1 counted: 10 * 3 = 30
    assert project.quality_indicator() == 30

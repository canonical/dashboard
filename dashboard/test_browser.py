from dataclasses import dataclass
from datetime import date
from typing import Any

import pytest

from playwright.sync_api import expect

from django.conf import settings
from django.contrib.auth.models import User
from django.urls import reverse

from framework.models import Condition, Level, Objective, ObjectiveGroup, WorkCycle
from projects.models import Commitment, Project, ProjectObjectiveCondition


@dataclass(frozen=True)
class BrowserTestData:
    project: Project
    level_started: Level
    level_first_results: Level
    colourfulness_projectobjective: Any
    poc_speaks_pleasantly: ProjectObjectiveCondition
    poc_accepts_praise: ProjectObjectiveCondition
    poc_has_red: ProjectObjectiveCondition
    poc_is_striated: ProjectObjectiveCondition
    poc_is_dappled: ProjectObjectiveCondition
    commitment_agree_started_2022: Commitment
    commitment_agree_started_2025: Commitment
    commitment_colour_first_results_2026: Commitment


@pytest.fixture
def browser_test_data(transactional_db):
    # Create the smallest object graph needed by the browser tests.

    User.objects.create_superuser("superuser", "superuser@example.com", "superuser")

    level_started = Level.objects.create(name="Started", value=1)
    level_first_results = Level.objects.create(name="First results", value=2)

    group_human = ObjectiveGroup.objects.create(name="Human friendliness")
    group_physical = ObjectiveGroup.objects.create(name="Physical characteristics")

    objective_agreeableness = Objective.objects.create(
        name="Agreeableness", group=group_human, weight=1
    )
    objective_colourfulness = Objective.objects.create(
        name="Colourfulness", group=group_physical, weight=1
    )
    objective_handling = Objective.objects.create(
        name="Handling", group=group_human, weight=1
    )

    condition_speaks_pleasantly = Condition.objects.create(
        name="Speaks pleasantly",
        objective=objective_agreeableness,
        level=level_started,
    )
    condition_accepts_praise = Condition.objects.create(
        name="Accepts praise and thanks with grace",
        objective=objective_agreeableness,
        level=level_first_results,
    )

    condition_has_blue = Condition.objects.create(
        name="Has blue",
        objective=objective_colourfulness,
        level=level_started,
    )
    condition_has_green = Condition.objects.create(
        name="Has green",
        objective=objective_colourfulness,
        level=level_started,
    )
    condition_has_red = Condition.objects.create(
        name="Has red",
        objective=objective_colourfulness,
        level=level_started,
    )
    condition_is_striated = Condition.objects.create(
        name="Is striated",
        objective=objective_colourfulness,
        level=level_first_results,
    )
    condition_is_dappled = Condition.objects.create(
        name="Is dappled",
        objective=objective_colourfulness,
        level=level_first_results,
    )

    condition_handles_safely = Condition.objects.create(
        name="Handles safely",
        objective=objective_handling,
        level=level_started,
    )

    workcycle_2022 = WorkCycle.objects.create(
        name="2022", timestamp=date(2022, 1, 1), is_current=False
    )
    workcycle_2025 = WorkCycle.objects.create(
        name="2025", timestamp=date(2025, 1, 1), is_current=False
    )
    workcycle_2026 = WorkCycle.objects.create(
        name="2026", timestamp=date(2026, 1, 1), is_current=True
    )

    project = Project.objects.create(
        name="Test Project", last_review=date(2024, 12, 16)
    )

    poc_speaks_pleasantly = ProjectObjectiveCondition.objects.get(
        project=project,
        objective=objective_agreeableness,
        condition=condition_speaks_pleasantly,
    )
    poc_accepts_praise = ProjectObjectiveCondition.objects.get(
        project=project,
        objective=objective_agreeableness,
        condition=condition_accepts_praise,
    )
    poc_has_blue = ProjectObjectiveCondition.objects.get(
        project=project,
        objective=objective_colourfulness,
        condition=condition_has_blue,
    )
    poc_has_green = ProjectObjectiveCondition.objects.get(
        project=project,
        objective=objective_colourfulness,
        condition=condition_has_green,
    )
    poc_has_red = ProjectObjectiveCondition.objects.get(
        project=project,
        objective=objective_colourfulness,
        condition=condition_has_red,
    )
    poc_is_striated = ProjectObjectiveCondition.objects.get(
        project=project,
        objective=objective_colourfulness,
        condition=condition_is_striated,
    )
    poc_is_dappled = ProjectObjectiveCondition.objects.get(
        project=project,
        objective=objective_colourfulness,
        condition=condition_is_dappled,
    )
    poc_handles_safely = ProjectObjectiveCondition.objects.get(
        project=project,
        objective=objective_handling,
        condition=condition_handles_safely,
    )

    # Set only the statuses needed by test expectations.
    poc_speaks_pleasantly.status = "DO"
    poc_accepts_praise.status = ""
    poc_has_blue.status = "DO"
    poc_has_green.status = "DO"
    poc_has_red.status = ""
    poc_is_striated.status = ""
    poc_is_dappled.status = ""
    poc_handles_safely.status = "DO"
    for poc in (
        poc_speaks_pleasantly,
        poc_accepts_praise,
        poc_has_blue,
        poc_has_green,
        poc_has_red,
        poc_is_striated,
        poc_is_dappled,
        poc_handles_safely,
    ):
        poc.save(update_fields=["status"])

    commitment_agree_started_2022 = Commitment.objects.get(
        project=project,
        objective=objective_agreeableness,
        level=level_started,
        work_cycle=workcycle_2022,
    )
    commitment_agree_started_2025 = Commitment.objects.get(
        project=project,
        objective=objective_agreeableness,
        level=level_started,
        work_cycle=workcycle_2025,
    )
    commitment_agree_started_2026 = Commitment.objects.get(
        project=project,
        objective=objective_agreeableness,
        level=level_started,
        work_cycle=workcycle_2026,
    )
    commitment_colour_started_2026 = Commitment.objects.get(
        project=project,
        objective=objective_colourfulness,
        level=level_started,
        work_cycle=workcycle_2026,
    )
    commitment_colour_first_results_2026 = Commitment.objects.get(
        project=project,
        objective=objective_colourfulness,
        level=level_first_results,
        work_cycle=workcycle_2026,
    )
    commitment_handling_started_2026 = Commitment.objects.get(
        project=project,
        objective=objective_handling,
        level=level_started,
        work_cycle=workcycle_2026,
    )

    commitment_agree_started_2022.committed = False
    commitment_agree_started_2025.committed = True
    commitment_agree_started_2026.committed = True
    commitment_colour_started_2026.committed = True
    commitment_colour_first_results_2026.committed = False
    commitment_handling_started_2026.committed = True
    for commitment in (
        commitment_agree_started_2022,
        commitment_agree_started_2025,
        commitment_agree_started_2026,
        commitment_colour_started_2026,
        commitment_colour_first_results_2026,
        commitment_handling_started_2026,
    ):
        commitment.save(update_fields=["committed"])

    colourfulness_projectobjective = poc_has_red.projectobjective()

    return BrowserTestData(
        project=project,
        level_started=level_started,
        level_first_results=level_first_results,
        colourfulness_projectobjective=colourfulness_projectobjective,
        poc_speaks_pleasantly=poc_speaks_pleasantly,
        poc_accepts_praise=poc_accepts_praise,
        poc_has_red=poc_has_red,
        poc_is_striated=poc_is_striated,
        poc_is_dappled=poc_is_dappled,
        commitment_agree_started_2022=commitment_agree_started_2022,
        commitment_agree_started_2025=commitment_agree_started_2025,
        commitment_colour_first_results_2026=commitment_colour_first_results_2026,
    )


def project_url(live_server, project, anchor=None):
    # Tabs are hash-based; objective controls are only visible when their tab is active.
    url = f"{live_server.url}{reverse('projects:project', None, [project.id])}"
    if anchor:
        return f"{url}#{anchor}"
    return url


@pytest.fixture
def page(page, client, live_server, browser_test_data):
    # Provide a Playwright page logged in to Django's live server.

    client.login(username="superuser", password="superuser")
    cookie = client.cookies[settings.SESSION_COOKIE_NAME]

    page.context.add_cookies(
        [
            {
                "name": settings.SESSION_COOKIE_NAME,
                "value": cookie.value,
                "url": live_server.url,
            }
        ]
    )

    yield page

    # Let pending HTMX/live-server requests settle before pytest-django flushes SQLite.
    try:
        page.wait_for_load_state("networkidle", timeout=5000)
    except Exception:
        # The page can already be closing during fixture teardown.
        pass


@pytest.mark.parametrize(
    "condition_key,initial_status,target_status,toggle_action",
    [
        # A condition already marked as done can be unset.
        pytest.param("poc_speaks_pleasantly", "DO", "", "uncheck", id="done-to-empty"),
        # A previously unset condition can be marked as done.
        pytest.param("poc_accepts_praise", "", "DO", "check", id="empty-to-done"),
    ],
)
def test_toggling_conditions(
    page,
    live_server,
    browser_test_data,
    condition_key,
    initial_status,
    target_status,
    toggle_action,
):
    # Check that condition toggles persist each status transition.

    project = browser_test_data.project
    # Open the objective tab that contains the condition toggles used in this test.
    page.goto(project_url(live_server, project, "agreeableness"))

    condition = getattr(browser_test_data, condition_key)
    assert (
        ProjectObjectiveCondition.objects.get(pk=condition.pk).status == initial_status
    )

    projectobjective = condition.projectobjective()

    toggle = page.get_by_test_id(f"toggle_condition_{condition.id}")
    expect(toggle).to_be_visible()
    with (
        page.expect_response(
            f"**/action_toggle_condition/{condition.id}?status={initial_status}&target=done"
        ),
        page.expect_response(f"**/status_projectobjective/{projectobjective.id}"),
        page.expect_response(f"**/status_projects_commitment/{project.id}"),
    ):
        getattr(toggle, toggle_action)()
    page.wait_for_load_state("networkidle")

    condition.refresh_from_db()
    assert condition.status == target_status


@pytest.mark.parametrize(
    "commitment_key,initial_committed,toggle_action,target_committed",
    [
        # A not-yet committed level can be committed.
        pytest.param(
            "commitment_agree_started_2022",
            False,
            "check",
            True,
            id="uncommitted-to-committed",
        ),
        # An already committed level can be uncommitted.
        pytest.param(
            "commitment_agree_started_2025",
            True,
            "uncheck",
            False,
            id="committed-to-uncommitted",
        ),
    ],
)
def test_toggling_commitments(
    page,
    live_server,
    browser_test_data,
    commitment_key,
    initial_committed,
    toggle_action,
    target_committed,
):
    # Check that commitment toggles persist each committed-state transition.

    project = browser_test_data.project
    # Open the objective tab that contains commitment toggles for Agreeableness.
    page.goto(project_url(live_server, project, "agreeableness"))

    commitment = getattr(browser_test_data, commitment_key)
    assert Commitment.objects.get(pk=commitment.pk).committed == initial_committed

    toggle = page.get_by_test_id(f"toggle_commitment_{commitment.id}")
    expect(toggle).to_be_visible()
    with (
        page.expect_response(f"**/action_toggle_commitment/{commitment.id}"),
        page.expect_response(f"**/status_projects_commitment/{project.id}"),
    ):
        getattr(toggle, toggle_action)()
    page.wait_for_load_state("networkidle")

    commitment.refresh_from_db()
    assert commitment.committed == target_committed


def check_condition_for_status(page, projectobjective_id, condition_id, project_id):
    with (
        page.expect_response(f"**/status_projectobjective/{projectobjective_id}"),
        page.expect_response(f"**/status_projects_commitment/{project_id}"),
    ):
        page.get_by_test_id(f"toggle_condition_{condition_id}").check()
    page.wait_for_load_state("networkidle")


@pytest.mark.parametrize(
    "condition_keys,status_level_key,status_text",
    [
        # Meeting the first-level condition sets status to Started.
        pytest.param(
            ["poc_has_red"], "level_started", "Started", id="reach-started-level"
        ),
        # Meeting all first-results conditions raises status to First results.
        pytest.param(
            ["poc_has_red", "poc_is_striated", "poc_is_dappled"],
            "level_first_results",
            "First results",
            id="reach-first-results-level",
        ),
    ],
)
def test_status(
    page,
    live_server,
    browser_test_data,
    condition_keys,
    status_level_key,
    status_text,
):
    # Check that objective status follows the highest reached level.

    project = browser_test_data.project
    projectobjective = browser_test_data.colourfulness_projectobjective
     # Activate the Colourfulness tab so the condition controls are interactable.
    page.goto(project_url(live_server, project, "colourfulness"))

    has_red = browser_test_data.poc_has_red
    assert has_red.projectobjective().project == project
    assert has_red.status == ""
    assert has_red.projectobjective().status is None
    expect(
        page.get_by_test_id(f"projectobjective_status_{projectobjective.id}")
    ).to_have_text("")

    for condition_key in condition_keys:
        check_condition_for_status(
            page,
            projectobjective.id,
            getattr(browser_test_data, condition_key).id,
            project.id,
        )

    final_condition = getattr(browser_test_data, condition_keys[-1])
    assert final_condition.projectobjective().status == getattr(
        browser_test_data, status_level_key
    )
    expect(
        page.get_by_test_id(f"projectobjective_status_{projectobjective.id}")
    ).to_have_text(status_text)


def csv_from_commitment_table(page):
    # Convert the commitments table to CSV.
    row_text = []
    rows = page.locator("table#commitment-table tr")
    for row_index in range(1, rows.count()):
        row = rows.nth(row_index)
        row_values = []
        cells = row.locator("td")
        for cell_index in range(cells.count()):
            cell = cells.nth(cell_index)
            checkbox = cell.locator("input[type='checkbox']")
            if checkbox.count() > 0:
                row_values.append("Y" if checkbox.is_checked() else "N")
            else:
                row_values.append(cell.inner_text().strip())
        row_text.append(",".join(row_values))
    return "\n".join(row_text)


def assert_commitment_table_rows(page, expected_rows):
    page.wait_for_load_state("networkidle")
    actual_rows = csv_from_commitment_table(page).splitlines()
    assert sorted(actual_rows) == sorted(expected_rows)


def apply_commitment_table_operation(page, project_id, browser_test_data, operation):
    operation_type, data_key = operation
    obj = getattr(browser_test_data, data_key)
    toggle_kind = "condition" if operation_type == "condition" else "commitment"

    if operation_type == "condition":
        projectobjective_id = obj.projectobjective().id
        with (
            page.expect_response(f"**/action_toggle_condition/{obj.id}**"),
            page.expect_response(f"**/status_projects_commitment/{project_id}"),
            page.expect_response(f"**/status_projectobjective/{projectobjective_id}"),
        ):
            page.get_by_test_id(f"toggle_{toggle_kind}_{obj.id}").check()
    else:
        with (
            page.expect_response(f"**/action_toggle_commitment/{obj.id}"),
            page.expect_response(f"**/status_projects_commitment/{project_id}"),
        ):
            page.get_by_test_id(f"toggle_{toggle_kind}_{obj.id}").check()
    page.wait_for_load_state("networkidle")


@pytest.mark.parametrize(
    "operations,expected_rows",
    [
        # Baseline overview before additional interaction.
        pytest.param(
            [],
            [
                "Agreeableness,Started,Y",
                "Colourfulness,Started,N",
                "Handling,Started,Y",
            ],
            id="baseline-overview",
        ),
        # Adding a first-results commitment adds a new row, still unmet.
        pytest.param(
            [("commitment", "commitment_colour_first_results_2026")],
            [
                "Agreeableness,Started,Y",
                "Colourfulness,Started,N",
                "Colourfulness,First results,N",
                "Handling,Started,Y",
            ],
            id="first-results-commitment-added",
        ),
        # Once Has red is done, Started is met while First results is still unmet.
        pytest.param(
            [
                ("commitment", "commitment_colour_first_results_2026"),
                ("condition", "poc_has_red"),
            ],
            [
                "Agreeableness,Started,Y",
                "Colourfulness,Started,Y",
                "Colourfulness,First results,N",
                "Handling,Started,Y",
            ],
            id="started-level-now-met",
        ),
        # After all first-results conditions are done, First results also becomes met.
        pytest.param(
            [
                ("commitment", "commitment_colour_first_results_2026"),
                ("condition", "poc_has_red"),
                ("condition", "poc_is_striated"),
                ("condition", "poc_is_dappled"),
            ],
            [
                "Agreeableness,Started,Y",
                "Colourfulness,Started,Y",
                "Colourfulness,First results,Y",
                "Handling,Started,Y",
            ],
            id="first-results-level-now-met",
        ),
    ],
)
def test_commitment_table(
    page, live_server, browser_test_data, operations, expected_rows
):
    # Check that commitment summary rows reflect the current toggled state.

    project = browser_test_data.project
    page.goto(project_url(live_server, project))

    if operations:
        # Switch to the objective tab to trigger updates that refresh the summary table.
        page.goto(project_url(live_server, project, "colourfulness"))
        for operation in operations:
            apply_commitment_table_operation(
                page, project.id, browser_test_data, operation
            )

    assert_commitment_table_rows(page, expected_rows)


def test_last_review(page, live_server, browser_test_data):
    project = browser_test_data.project
    page.goto(project_url(live_server, project))
    expect(page.locator("#id_last_review")).to_have_value("2024-12-16")

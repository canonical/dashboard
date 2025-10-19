from django.contrib import admin
from django.urls import include, path
from .views import (
    ProjectListView,
    project,
    action_toggle_commitment,
    action_toggle_condition,
    action_select_reason,
    project_basic_form_save,
    status_projects_commitment,
    status_projectobjective,
)

app_name = "projects"
urlpatterns = [
    path("", ProjectListView.as_view(), name="project_list"),
    path("<int:id>/", project, name="project"),
    # forms
    path(
        "update/<int:project_id>",
        project_basic_form_save,
        name="project_basic_form_save",
    ),
    # action views
    path(
        "action_toggle_commitment/<int:commitment_id>",
        action_toggle_commitment,
        name="action_toggle_commitment",
    ),
    path(
        "action_toggle_condition/<int:condition_id>",
        action_toggle_condition,
        name="action_toggle_condition",
    ),
    path(
        "action_select_reason/<str:projectobjective_id>",
        action_select_reason,
        name="action_select_reason",
    ),
    # status views
    path(
        "status_projects_commitment/<int:project_id>",
        status_projects_commitment,
        name="status_projects_commitment",
    ),
    path(
        "status_projectobjective/<int:projectobjective_id>",
        status_projectobjective,
        name="status_projectobjective",
    ),
]

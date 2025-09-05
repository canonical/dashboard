from django.contrib import admin
from django.urls import include, path
from .views import (
    ProjectDetailView,
    ProjectListView,
    action_toggle_commitment,
    action_toggle_condition,
    project_basic_form_save
)

app_name = "projects"
urlpatterns = [
    path("", ProjectListView.as_view(), name="project_list"),

    path(
        "<int:project_id>/update",
        project_basic_form_save,
        name="project_basic_form_save",
    ),

    path("<int:pk>/", ProjectDetailView.as_view(), name="project_detail"),

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
]

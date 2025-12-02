from django.contrib import admin
from django.urls import include, path
from .views import admin_apply_qis

app_name = "framework"
urlpatterns = [
    # admin
    path(
        "admin_apply_qis/<int:workcycle_id>",
        admin_apply_qis,
        name="admin_apply_qis"
    ),
]

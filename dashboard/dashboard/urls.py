from django.contrib import admin
from django.urls import include, path
from projects.views import ProjectDetailView, ProjectListView, action_toggle_commitment

urlpatterns = [
    path("admin/doc/", include("django.contrib.admindocs.urls")),
    path("admin/", admin.site.urls),
    path("__reload__/", include("django_browser_reload.urls")),
    path("", include("projects.urls")),
]

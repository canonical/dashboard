from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    # basic Django
    path("admin/doc/", include("django.contrib.admindocs.urls")),
    path("admin/", admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),

    # Dashboard
    path("", include("projects.urls")),
    path("", include("framework.urls")),

    # utilities
    path('tinymce/', include('tinymce.urls')),
]

urlpatterns.extend([
    path("__reload__/", include("django_browser_reload.urls")),
])


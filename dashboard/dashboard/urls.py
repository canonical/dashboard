from django.contrib import admin
from django.urls import include, path
from mozilla_django_oidc import views as oidc_views

urlpatterns = [
    # basic Django
    path("admin/doc/", include("django.contrib.admindocs.urls")),
    path("admin/", admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
    
    # OIDC URLs
    path("oidc/authenticate", oidc_views.OIDCAuthenticationRequestView.as_view(), name="oidc_authentication_init"),
    path("oidc/callback", oidc_views.OIDCAuthenticationCallbackView.as_view(), name="oidc_authentication_callback"),
    path("oidc/logout/", oidc_views.OIDCLogoutView.as_view(), name="oidc_logout"),

    # Dashboard
    path("", include("projects.urls")),
    path("", include("framework.urls")),

    # utilities
    path('tinymce/', include('tinymce.urls')),
]

urlpatterns.extend([
    path("__reload__/", include("django_browser_reload.urls")),
])


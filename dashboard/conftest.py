import sys
import types

from django.http import HttpResponse


# Creat a "fake" mozilla_django_oidc.views so that tests will run,
# even if mozilla_django_oidc is not available at import time for
# tests.

if "mozilla_django_oidc" not in sys.modules:
    oidc_module = types.ModuleType("mozilla_django_oidc")
    oidc_views_module = types.ModuleType("mozilla_django_oidc.views")

    class _DummyOIDCView:
        @classmethod
        def as_view(cls):
            def _view(request, *args, **kwargs):
                return HttpResponse("")

            return _view

    oidc_views_module.OIDCAuthenticationRequestView = _DummyOIDCView
    oidc_views_module.OIDCAuthenticationCallbackView = _DummyOIDCView
    oidc_views_module.OIDCLogoutView = _DummyOIDCView
    oidc_module.views = oidc_views_module
    sys.modules["mozilla_django_oidc"] = oidc_module
    sys.modules["mozilla_django_oidc.views"] = oidc_views_module

"""
Custom authentication decorators and mixins that conditionally require login
based on OIDC configuration.
"""
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from functools import wraps


class ConditionalLoginRequiredMixin(LoginRequiredMixin):
    """
    Mixin that requires login only when OIDC is configured.
    When OIDC is not configured, allows anonymous access.
    """
    def dispatch(self, request, *args, **kwargs):
        # Only require login if OIDC is configured
        if settings.OIDC_RP_CLIENT_ID:
            return super().dispatch(request, *args, **kwargs)
        # Otherwise, skip login requirement
        return super(LoginRequiredMixin, self).dispatch(request, *args, **kwargs)


def conditional_login_required(view_func):
    """
    Decorator that requires login only when OIDC is configured.
    When OIDC is not configured, allows anonymous access.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Only require login if OIDC is configured
        if settings.OIDC_RP_CLIENT_ID:
            return login_required(view_func)(request, *args, **kwargs)
        return view_func(request, *args, **kwargs)
    return wrapper

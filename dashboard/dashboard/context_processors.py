"""Context processors for dashboard templates."""
from django.conf import settings


def oidc_settings(request):
    """Make OIDC configuration status available in templates."""
    return {
        'oidc_configured': bool(settings.OIDC_RP_CLIENT_ID),
    }

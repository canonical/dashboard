from django import template
from projects.models import Commitment

register = template.Library()


@register.simple_tag
def work_cycle_commitment(work_cycle, project, objective, level):
    return Commitment.objects.get(
        work_cycle=work_cycle, project=project, objective=objective, level=level
    ).committed


@register.simple_tag
def pack(*args):
    return zip(*args)


@register.filter
def display_name(user):
    """Return a friendly name for displaying in the UI; needed because OIDC usernames are hashes."""
    if not user:
        return ""
    return user.email or user.username

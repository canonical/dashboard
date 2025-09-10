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

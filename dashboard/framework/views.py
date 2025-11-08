from django.shortcuts import render

from django.urls import reverse
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect

from projects.models import Project, QI


def admin_apply_qis(request, workcycle_id):
    qis = QI.objects.filter(workcycle_id=workcycle_id)
    for qi in qis:
        qi.value = qi.project.quality_indicator
    QI.objects.bulk_update(qis, ["value"])
    messages.info(request, 'Copied current QI values.')
    return HttpResponseRedirect(
       reverse('admin:framework_workcycle_change', args=[workcycle_id])
    )

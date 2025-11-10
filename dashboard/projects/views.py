import datetime
from django.shortcuts import render, HttpResponse, HttpResponseRedirect
from django.views.generic import ListView
from django.views.decorators.http import require_http_methods
from django.forms import inlineformset_factory
from django.http import QueryDict
from django.contrib.auth.decorators import permission_required
from django.contrib import messages
from django.urls import reverse


from .models import (
    Project,
    Commitment,
    ProjectObjectiveCondition,
    ProjectObjective,
)
from . import forms

from framework.models import WorkCycle, Objective, ObjectiveGroup, Reason


class ProjectListView(ListView):
    model = Project

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        context["workcycle_list"] = WorkCycle.objects.all()
        context["workcycle_count"] = WorkCycle.objects.count()
        context["objective_list"] = Objective.objects.all()
        context["objective_count"] = Objective.objects.count()
        context["column_count"] = (
            Objective.objects.count() + WorkCycle.objects.count() + 6
        )
        context["quality_cols_count"] = 4 + WorkCycle.objects.count()

        return context


def project(request, id):

    project = Project.objects.get(id=id)

    basics_form = forms.ProjectDetailForm(instance=project)
    if not request.user.has_perm('projects.change_project'):
        for fieldname in basics_form.fields:
            basics_form.fields[fieldname].disabled = True

    commitments = Commitment.objects.filter(project=project)


    ProjectObjectiveInlineFormSet = inlineformset_factory(
        Project,
        ProjectObjective,
        form=forms.ProjectObjectiveForm,
        edit_only=True,
        can_delete=False,
        extra=0,
    )

    return render(
        request,
        "projects/project.html",
        {
            "project": project,
            "work_cycles": WorkCycle.objects.all(),
            "workcycle_count": WorkCycle.objects.count(),
            "objectivegroup_list": ObjectiveGroup.objects.all(),
            "objective_list": Objective.objects.all(),
            "objective_count": Objective.objects.count(),
            "commitments": commitments,
            "current_commitments": commitments.filter(
                work_cycle__is_current=True, committed=True
            ),
            "unstarted_reasons": Reason.objects.all(),
            "basics_form": basics_form,
            "projectobjectives_formset": ProjectObjectiveInlineFormSet(
                instance=project
            ),
        },
    )


# detail view status methods

@require_http_methods(["GET"])
def status_projects_commitment(request, project_id):

    project = Project.objects.get(id=project_id)
    current_commitments = Commitment.objects.filter(
        project=project, work_cycle__is_current=True, committed=True
    )

    return render(
        request,
        "projects/partial_project_detail_commitments.html",
        {
            "project": project,
            "current_commitments": current_commitments,
        },
    )

    return render(
        request,
        "projects/partial_project_detail_commitments.html",
        {"project": project, "current_commitments": current_commitments},
    )

@require_http_methods("GET")
def status_projectobjective(request, projectobjective_id):

    projectobjective = ProjectObjective.objects.get(id=projectobjective_id)

    return render(
        request,
        "projects/partial_project_detail_objectivestatus.html",
        {
            "projectobjective": projectobjective,
            "unstarted_reasons": Reason.objects.all(),
        },
    )

# list view status methods

@require_http_methods("GET")
def status_dashboardprojectobjective(request, projectobjective_id):
    projectobjective = ProjectObjective.objects.get(id=projectobjective_id)

    return render(
        request,
        "projects/partial_project_list_objectivestatus.html",
        {
            "projectobjective": projectobjective,
        },
    )

def project_row(request, project_id):
    project = Project.objects.get(id=project_id)

    project.projectobjectives = project.projectobjective_set.all().values(
        "objective__name",
        "id",
        "level_achieved__name",
        "unstarted_reason__name"
    )

    return render(
        request,
        "projects/partial_project_list_row.html",
        {
            "project": project,
        }
    )



# action methods

@permission_required("projects.change_commitment")
@require_http_methods(["PUT"])
def action_toggle_commitment(request, commitment_id):
    commitment = Commitment.objects.get(id=commitment_id)
    commitment.committed = not commitment.committed
    commitment.save()

    return HttpResponse("")


@permission_required("projects.change_projectobjectivecondition")
@require_http_methods(["PUT"])
def action_toggle_condition(request, condition_id):
    condition = ProjectObjectiveCondition.objects.get(id=condition_id)
    target = request.GET["target"]
    status = request.GET["status"]

    match target:
        case "done":
            if status == "DO":
                condition.status = ""
            else:
                condition.status = "DO"
        case "candidate":
            if status == "CA":
                condition.status = ""
            else:
                condition.status = "CA"
        case "not-applicable":
            if status == "NA":
                condition.status = ""
            else:
                condition.status = "NA"

    condition.save()

    return render(
        request,
        "projects/partial_project_detail_condition.html",
        {"condition": condition, "workcycle_count": WorkCycle.objects.count()},
    )

@permission_required("projects.change_projectobjective")
@require_http_methods(["PUT"])
def action_select_reason(request, projectobjective_id):
    projectobjective = ProjectObjective.objects.get(id=projectobjective_id)

    value = QueryDict(request.body)["ifnotstarted"]
    if value:
        projectobjective.unstarted_reason = Reason.objects.get(id=int(value))
    else:
        projectobjective.unstarted_reason = None
    projectobjective.save()

    return HttpResponse("")


# form methods

@require_http_methods(["POST"])
def project_basic_form_save(request, project_id):
    instance = Project.objects.get(id=project_id)
    form = forms.ProjectDetailForm(request.POST, instance=instance)
    form.save()
    return render(
        request,
        "projects/partial_project_detail_basics.html",
        {"basics_form": form, "project": instance},
    )


# admin methods

def admin_recalculate_all_levels(request):
    for projectobjective in ProjectObjective.objects.all():
        projectobjective.save()

    messages.info(request, 'Recalculated all levels.')
    return HttpResponseRedirect(
       reverse('admin:index')
    )

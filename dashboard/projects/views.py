import datetime
from django.shortcuts import render, HttpResponse
from django.views.generic import ListView
from django.views.decorators.http import require_http_methods
from django.forms import inlineformset_factory
from django.http import QueryDict
from django.contrib.auth.decorators import permission_required


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
        context["quality_cols_count"] = 3 + WorkCycle.objects.count()

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


# status methods


@require_http_methods(["GET"])
def status_projects_commitment(request, project_id):

    project = Project.objects.get(id=project_id)
    current_commitments = Commitment.objects.filter(
        project=project, work_cycle__is_current=True, committed=True
    )

    return render(
        request,
        "projects/partial_project_commitments.html",
        {
            "project": project,
            "current_commitments": current_commitments,
        },
    )

    return render(
        request,
        "projects/partial_project_commitments.html",
        {"project": project, "current_commitments": current_commitments},
    )

@require_http_methods("GET")
def status_projectobjective(request, projectobjective_id):

    projectobjective = ProjectObjective.objects.get(id=projectobjective_id)

    return render(
        request,
        "projects/partial_objectivestatus.html",
        {
            "projectobjective": projectobjective,
            "unstarted_reasons": Reason.objects.all(),
        },
    )


# action methods

@permission_required("projects.change_commitment")
@require_http_methods(["PUT"])
def action_toggle_commitment(request, commitment_id):
    commitment = Commitment.objects.get(id=commitment_id)
    commitment.committed = not commitment.committed
    commitment.save()

    return HttpResponse("")


@permission_required("projects.change_condition")
@require_http_methods(["PUT"])
def action_toggle_condition(request, condition_id):
    condition = ProjectObjectiveCondition.objects.get(id=condition_id)
    condition.done = not condition.done
    if condition.done:
        condition.not_applicable = False
        condition.candidate = False
    condition.save()

    return render(
        request,
        "projects/partial_condition.html",
        {"condition": condition, "workcycle_count": WorkCycle.objects.count()},
    )


@permission_required("projects.change_condition")
@require_http_methods(["PUT"])
def action_condition_toggle_candidate(request, condition_id):
    condition = ProjectObjectiveCondition.objects.get(id=condition_id)
    condition.candidate = not condition.candidate
    if condition.candidate:
        condition.not_applicable = False
        condition.done = False
    condition.save()

    return render(
        request,
        "projects/partial_condition.html",
        {"condition": condition, "workcycle_count": WorkCycle.objects.count()},
    )


@permission_required("projects.change_condition")
@require_http_methods(["PUT"])
def action_condition_toggle_not_applicable(request, condition_id):
    condition = ProjectObjectiveCondition.objects.get(id=condition_id)
    condition.not_applicable = not condition.not_applicable
    if condition.not_applicable:
        condition.candidate = False
        condition.done = False
    condition.save()

    return render(
        request,
        "projects/partial_condition.html",
        {"condition": condition, "workcycle_count": WorkCycle.objects.count()},
    )
    return HttpResponse("")


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
        "projects/partial_project_basics.html",
        {"basics_form": form, "project": instance},
    )

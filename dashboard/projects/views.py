import json
from django.db.models import F, Sum
from django.shortcuts import render, HttpResponse, HttpResponseRedirect
from django.views.generic import ListView
from django.views.decorators.http import require_http_methods
from django.forms import inlineformset_factory
from django.http import QueryDict
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import permission_required
from django.contrib import messages
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify

from dashboard.auth_decorators import ConditionalLoginRequiredMixin, conditional_login_required

from .models import (
    Project,
    Commitment,
    ProjectObjectiveCondition,
    ProjectObjective,
)
from . import forms

from framework.models import WorkCycle, Objective, ObjectiveGroup, Reason


class ProjectListView(ConditionalLoginRequiredMixin, ListView):
    model = Project

    def get_queryset(self):
        return super().get_queryset().select_related(
            "group", "agreement_status", "last_review_status"
        ).prefetch_related("qi_set__workcycle")

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)


        # Build a per-project objective map once to avoid repeated row-level lookups.
        pos_by_project = {}
        for po in ProjectObjective.objects.all().values(
            "project_id",
            "objective__name",
            "id",
            "level_achieved__name",
            "unstarted_reason__name",
        ):
            pos_by_project.setdefault(po["project_id"], []).append(po)

        projects = list(context["object_list"])
        project_ids = [project.id for project in projects]

        # Collect quality indicator totals in one grouped query.
        quality_indicator_by_project = {
            row["project_id"]: row["total"]
            for row in ProjectObjective.objects.filter(
                project_id__in=project_ids, level_achieved__isnull=False
            )
            .values("project_id")
            .annotate(total=Sum(F("level_achieved__value") * F("objective__weight")))
        }

        today = timezone.now().date()

        # Attach prepared values to each project so the template can render without extra ORM work.
        for project in projects:
            project.projectobjectives = pos_by_project.get(project.id, [])
            project.quality_history_values = [
                qi for qi in project.qi_set.all() if qi.workcycle.timestamp <= today
            ]
            project.quality_indicator_value = quality_indicator_by_project.get(
                project.id, 0
            )

        workcycle_list = list(WorkCycle.objects.filter(timestamp__lte=timezone.now().date()))
        objective_list = list(Objective.objects.all())
        workcycle_count = len(workcycle_list)
        objective_count = len(objective_list)

        context["workcycle_list"] = workcycle_list
        context["workcycle_count"] = workcycle_count
        context["objective_list"] = objective_list
        context["objective_count"] = objective_count
        context["column_count"] = objective_count + workcycle_count + 7
        context["quality_cols_count"] = 4 + workcycle_count

        return context


@conditional_login_required
def project(request, id):

    project = Project.objects.get(id=id)

    can_edit_project = request.user.has_perm("projects.change_project")
    basics_form = forms.ProjectDetailForm(instance=project)
    if not can_edit_project:
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
            "current_work_cycle_name": WorkCycle.name_of_current(),
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
            "can_edit_project": can_edit_project,
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
            "current_work_cycle_name": WorkCycle.name_of_current(),
            "current_commitments": current_commitments,
        },
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


# action methods

@permission_required("projects.change_commitment")
@require_http_methods(["PUT"])
def action_toggle_commitment(request, commitment_id):
    commitment = Commitment.objects.get(id=commitment_id)
    commitment.committed = not commitment.committed
    commitment.save()

    # Include a custom event in the HTTP header.
    # On the project detail page, the commitments table will trigger a refresh when the page sees
    # the event.
    # See https://htmx.org/headers/hx-trigger/
    response = HttpResponse("")
    response["HX-Trigger-After-Swap"] = "updateCommitment"
    return response


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

    response = render(
        request,
        "projects/partial_project_detail_condition.html",
        {"condition": condition, "workcycle_count": WorkCycle.objects.count()},
    )
    # Include a custom event in the HTTP header.
    # On the project detail page, the commitments table and the PO status will trigger a refresh
    # when the page sees the event. We want to be able to target a specific PO status, so we
    # attach a value (the PO name) to the event.
    # See https://htmx.org/headers/hx-trigger/
    response["HX-Trigger-After-Swap"] = json.dumps({
        "updateCondition": slugify(condition.projectobjective().name()),
    })
    return response


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

@permission_required("projects.change_project")
@require_http_methods(["POST"])
def project_basic_form_save(request, project_id):
    instance = Project.objects.get(id=project_id)
    form = forms.ProjectDetailForm(request.POST, instance=instance)
    review_fields = {"agreement_status", "last_review", "last_review_status"}
    changed_review_fields = review_fields.intersection(form.changed_data)

    instance = form.save(commit=False)
    if changed_review_fields:
        instance.updated_by = request.user
        instance.updated_at = timezone.now()
    instance.save()
    return render(
        request,
        "projects/partial_project_detail_basics.html",
        {
            "basics_form": form,
            "project": instance,
            "can_edit_project": request.user.has_perm("projects.change_project"),
        },
    )


# admin methods

@staff_member_required
@require_http_methods(["GET"])
def admin_recalculate_all_levels(request):
    for projectobjective in ProjectObjective.objects.all():
        projectobjective.save()

    messages.info(request, 'Recalculated all levels.')
    return HttpResponseRedirect(
       reverse('admin:index')
    )

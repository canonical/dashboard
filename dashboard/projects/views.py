import datetime
from django.shortcuts import render, HttpResponse
from django.views.generic import ListView, DetailView, FormView
from django.views.decorators.http import require_http_methods

from .models import (
    Project,
    LevelCommitment,
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


class ProjectDetailView(DetailView):
    model = Project

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        work_cycles = WorkCycle.objects.all()

        context["work_cycles"] = work_cycles
        context["work_cycle_count"] = work_cycles.count()

        context["objectivegroup_list"] = ObjectiveGroup.objects.all()

        context["objective_list"] = Objective.objects.all()
        context["objective_count"] = Objective.objects.count()

        commitments = LevelCommitment.objects.filter(project=self.object)
        context["commitments"] = commitments

        context["current_commitments"] = commitments.filter(work_cycle__is_current=True, committed=True)



        context["unstarted_reasons"] = Reason.objects.all()

        # context["form"] = forms.ProjectDetailForm()

        return context


@require_http_methods(["PUT"])
def action_toggle_commitment(request, commitment_id):
    commitment = LevelCommitment.objects.get(id=commitment_id)
    commitment.committed = not commitment.committed
    commitment.save()
    return HttpResponse("")


@require_http_methods(["PUT"])
def action_toggle_condition(request, condition_id):
    condition = ProjectObjectiveCondition.objects.get(id=condition_id)
    condition.done = not condition.done
    condition.save()
    return render(
        request,
        "projects/partial_objectivestatus.html",
        {"projectobjective": condition.projectobjective},
    )

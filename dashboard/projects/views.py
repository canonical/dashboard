from django.shortcuts import render
from django.views.generic import ListView, DetailView

from .models import Project, Objective, LevelCommitment
from framework.models import WorkCycle


class ProjectListView(ListView):
    model = Project

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        context["workcycle_list"] = WorkCycle.objects.all()
        context["workcycle_count"] = WorkCycle.objects.count()

        context["objective_list"] = Objective.objects.all()
        context["objective_count"] = Objective.objects.count()

        context["column_count"] = Objective.objects.count() + WorkCycle.objects.count() + 6

        context["quality_cols_count"] = 3 + WorkCycle.objects.count()

        return context


class ProjectDetailView(DetailView):
    model = Project

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        work_cycles = WorkCycle.objects.all()

        context["work_cycles"] = work_cycles
        context["work_cycle_count"] = work_cycles.count()

        context["objective_list"] = Objective.objects.all()
        context["objective_count"] = Objective.objects.count()

        context["commitments"] = LevelCommitment.objects.filter(project=self.object)

        return context

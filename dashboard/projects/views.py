import datetime
from django.shortcuts import render
from django.views.generic import ListView

from .models import Project, Objective
from framework.models import WorkCycle


class ProjectListView(ListView):
    model = Project

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        workcycles = WorkCycle.objects.filter(timestamp__lte=datetime.date.today())

        context["workcycle_list"] = workcycles
        context["objective_list"] = Objective.objects.all()

        context["workcycle_count"] = workcycles.count()
        context["objective_count"] = Objective.objects.count()
        context["column_count"] = Objective.objects.count() + workcycles.count() + 6

        context["quality_cols_count"] = 3 + workcycles.count()



        return context

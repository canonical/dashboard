from django.shortcuts import render
from django.views.generic import ListView

from .models import Project, Objective


class ProjectListView(ListView):
    model = Project

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["objective_list"] = Objective.objects.all()
        return context

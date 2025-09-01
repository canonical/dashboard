from . import models
from django.forms import ModelForm


class ProjectDetailForm(ModelForm):
    class Meta:
        model = models.Project
        fields = ["name"]

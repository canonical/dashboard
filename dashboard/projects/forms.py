from . import models
from django.forms import ModelForm


class ProjectDetailForm(ModelForm):
    class Meta:
        model = models.Project
        fields = [
            "name",
            "group",
            "owner",
            "driver",
            "last_review",
            "last_review_status",
        ]

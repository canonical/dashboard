from . import models
from django.forms import ModelForm
from django.forms import inlineformset_factory


class ProjectDetailForm(ModelForm):
    class Meta:
        model = models.Project
        fields = [
            "name",
            "group",
            "owner",
            "driver",
            "agreement_status",
            "last_review",
            "last_review_status",
        ]


class ProjectObjectiveForm(ModelForm):
    class Meta:
        model = models.ProjectObjective
        fields = ["unstarted_reason"]
        labels = {"unstarted_reason": ""}
        help_texts = {"unstarted_reason": ""}


class ProjectObjectiveConditionForm(ModelForm):
    class Meta:
        model = models.ProjectObjectiveCondition
        fields = ["done"]


class CommitmentForm(ModelForm):
    class Meta:
        model = models.Commitment
        fields = ["committed"]

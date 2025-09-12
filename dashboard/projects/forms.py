from . import models
from django import forms

class DatePickerInput(forms.DateInput):
    input_type = 'date'


class ProjectDetailForm(forms.ModelForm):

    class Meta:
        model = models.Project
        fields = [
            "name",
            "url",
            "group",
            "owner",
            "driver",
            "agreement_status",
            "last_review",
            "last_review_status",
        ]
        widgets = {
            'last_review' : DatePickerInput(),
        }

    # last_review = forms.DateField(widget=forms.DateInput)


class ProjectObjectiveForm(forms.ModelForm):
    class Meta:
        model = models.ProjectObjective
        fields = ["unstarted_reason"]
        labels = {"unstarted_reason": ""}
        help_texts = {"unstarted_reason": ""}


class ProjectObjectiveConditionForm(forms.ModelForm):
    class Meta:
        model = models.ProjectObjectiveCondition
        fields = ["done"]


class CommitmentForm(forms.ModelForm):
    class Meta:
        model = models.Commitment
        fields = ["committed"]

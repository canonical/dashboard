from datetime import date, timedelta

from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from framework.models import (
    Reason,
    Condition,
    Level,
    Objective,
    ProjectStatus,
    AgreementStatus,
    WorkCycle,
)


class ProjectGroup(models.Model):

    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Project(models.Model):

    name = models.CharField(max_length=200)
    group = models.ForeignKey(ProjectGroup, null=True, on_delete=models.SET_NULL)
    owner = models.CharField(
        help_text="Usually the engineering manager or director",
        max_length=200,
        blank=True,
        null=True,
    )
    driver = models.CharField(
        help_text="Usually a technical author", max_length=200, blank=True, null=True
    )
    objectives = models.ManyToManyField(Objective, through="ProjectObjective")
    last_review = models.DateField(null=True, blank=True)
    last_review_status = models.ForeignKey(
        ProjectStatus, null=True, on_delete=models.SET_NULL
    )
    agreement_status = models.ForeignKey(
        AgreementStatus, null=True, on_delete=models.SET_NULL
    )

    def __str__(self):
        return self.name

    def save(self, **kwargs):
        super().save(**kwargs)

        # when a new Project is added propagate it to all existing Objectives
        for objective in Objective.objects.exclude(project=self):
            ProjectObjective.objects.create(project=self, objective=objective)

            # and propagate the Conditions to the ProjectObjective
            for condition in Condition.objects.filter(objective=objective):
                ProjectObjectiveCondition.objects.get_or_create(
                    project=self, objective=objective, condition=condition
                )

        # make sure there's a QI object for this Project for each WorkCycle
        for work_cycle in WorkCycle.objects.all():
            QI.objects.get_or_create(workcycle=work_cycle, project=self)

            # make sure there is a LevelCommitment for each WorkCycle/Level/Objective for the Project
            for objective in Objective.objects.filter(project=self):
                for level in Level.objects.all():
                    l = LevelCommitment.objects.get_or_create(
                        work_cycle=work_cycle,
                        project=self,
                        objective=objective,
                        level=level,
                    )

    def get_absolute_url(self):
        return reverse("projects:project_detail", kwargs={"pk": self.pk})

    def quality_indicator(self):
        x = 0
        for po in self.projectobjective_set.all():
            # this is a horrendous way to solve the problem and there must be something more elegant
            try:
                x = x + po.status.value * po.objective.weight
            except AttributeError:
                pass
        return x

    def quality_history(self):
        return QI.objects.filter(project=self)

    def review_freshness(self):
        # consider using the database to define these values instead

        if self.last_review:
            if date.today() - self.last_review < timedelta(days=31):
                return "new"
            elif date.today() - self.last_review < timedelta(days=93):
                return "acceptable"
            elif date.today() - self.last_review < timedelta(days=186):
                return "overdue"
            else:
                return "unacceptable"

    class Meta:
        ordering = ["group", "name"]


class ProjectObjective(models.Model):

    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    objective = models.ForeignKey(Objective, on_delete=models.CASCADE)
    unstarted_reason = models.ForeignKey(
        Reason,
        on_delete=models.SET_NULL,
        help_text="Will be overridden by <em>Status</em> if appropriate",
        null=True,
        blank=True,
    )

    def __str__(self):
        return " > ".join((self.project.name, self.objective.name))

    def achieved_level(self):
        for level in reversed(Level.objects.all()):
            results = ProjectObjectiveCondition.objects.filter(
                project=self.project,
                objective=self.objective,
                condition__level=level,
            )
            if results.exists() and not results.filter(done=False).exists():
                return level

    def status(self):
        return self.achieved_level() or self.unstarted_reason

    # def status_slug(self):
    #     return slugify(self.status())

    def name(self):
        return self.objective.name

    def description(self):
        return self.objective.description

    def projectobjectiveconditions(self):
        return ProjectObjectiveCondition.objects.filter(
            project=self.project, objective=self.objective
        )

    def levelcommitments(self):
        return LevelCommitment.objects.filter(
            project=self.project, objective=self.objective
        )

    class Meta:
        ordering = ["project", "objective"]
        constraints = [
            models.UniqueConstraint(
                fields=["project", "objective"], name="unique_project_objective"
            )
        ]


class ProjectObjectiveCondition(models.Model):

    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    objective = models.ForeignKey(Objective, on_delete=models.CASCADE)
    condition = models.ForeignKey(Condition, on_delete=models.CASCADE)
    done = models.BooleanField(default=False)

    def projectobjective(self):
        return ProjectObjective.objects.get(
            project=self.project, objective=self.objective
        )

    def levelcommitments(self):
        return LevelCommitment.objects.filter(
            project=self.project, objective=self.objective, level=self.level()
        )

    def level(self):
        return self.condition.level

    def __str__(self):
        return " > ".join((self.project.name, self.objective.name, self.condition.name))

    def name(self):
        return self.condition.name

    class Meta:
        ordering = ["project", "objective", "condition"]
        constraints = [
            models.UniqueConstraint(
                fields=["project", "objective", "condition"],
                name="unique_project_objective_condition",
            )
        ]


class LevelCommitment(models.Model):
    # records a commitment, to a level of an objective of a project, for a particular work cycle

    work_cycle = models.ForeignKey(WorkCycle, on_delete=models.CASCADE)
    project = models.ForeignKey("Project", on_delete=models.CASCADE)
    objective = models.ForeignKey(Objective, on_delete=models.CASCADE)
    level = models.ForeignKey(Level, on_delete=models.CASCADE)
    committed = models.BooleanField(default=False)

    def __str__(self):
        return " > ".join(
            (
                self.project.name,
                self.objective.name,
                self.level.name,
                self.work_cycle.name,
            )
        )

    def projectobjective(self):
        return ProjectObjective.objects.get(
            project=self.project, objective=self.objective
        )

    def met(self):
        if self.projectobjective().achieved_level():
            return self.projectobjective().achieved_level().value >= self.level.value

    class Meta:
        ordering = [
            "objective",
            "level",
            "work_cycle",
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["project", "objective", "work_cycle", "level"],
                name="unique_level_attributes",
            )
        ]


class QI(models.Model):
    # a snapshot of a project's quality indication per WorkCycle
    project = models.ForeignKey("Project", on_delete=models.CASCADE)
    workcycle = models.ForeignKey(WorkCycle, on_delete=models.CASCADE)
    value = models.SmallIntegerField(default=0)

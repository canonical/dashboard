from datetime import date, timedelta
from django.db import models
from django.utils.text import slugify

from framework.models import ProjectStatus, WorkCycle, Level, Objective, Condition

NA = "na"
PLANNED = "PL"
STARTED = "ST"
DEFERRED = "DE"
BLOCKED = "BL"
INACTIVE = "IN"


class LevelCommitment(models.Model):
    # records a commitment, to a level of an objective of a project, for a particular work cycle

    work_cycle = models.ForeignKey(WorkCycle, on_delete=models.CASCADE)
    project_objective = models.ForeignKey("ProjectObjective", on_delete=models.CASCADE)
    committed = models.BooleanField(default=False)
    level = models.ForeignKey(Level, on_delete=models.CASCADE)

    class Meta:
        ordering = ["work_cycle", "level"]


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

    def __str__(self):
        return self.name

    def save(self, **kwargs):
        # required in order to ensure that when a new Project (row) is added to the dashboard,
        # all the existing Objectives (columns) are associated with it via ProjectObjectives;
        # in turn each ProjectObjective needs to have ProjectObjectiveConditions created for it.

        super().save(**kwargs)

        # For each Objective, create a ProjectObjective instance for this Project if missing
        for objective in Objective.objects.exclude(project=self):
            projectobjective = ProjectObjective(project=self, objective=objective)
            projectobjective.save()
            for condition in Condition.objects.filter(objective=objective):
                ProjectObjectiveCondition.objects.get_or_create(
                    condition=condition, projectobjective=projectobjective
                )

    def quality_indicator(self):
        x = 0
        for po in self.projectobjective_set.all():
            # this is a horrendous way to solve the problem and there must be something more elegant
            try:
                x = x + po.status().value * po.objective.weight
            except AttributeError:
                pass
        return x

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
    NA = "na"
    PLANNED = "PL"
    DEFERRED = "DE"
    BLOCKED = "BL"
    INACTIVE = "IN"

    STATUS_CHOICES = [
        (NA, "na"),
        (PLANNED, "Planned"),
        (DEFERRED, "Deferred"),
        (BLOCKED, "Blocked"),
        (INACTIVE, "Inactive"),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    objective = models.ForeignKey(Objective, on_delete=models.CASCADE)
    if_not_started = models.CharField(
        help_text="Will be overridden by <em>Status</em> if appropriate",
        max_length=2,
        choices=STATUS_CHOICES,
        null=True,
        blank=True,
    )

    work_cycles = models.ManyToManyField(WorkCycle, through=LevelCommitment)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["project", "objective"], name="unique_project_objective"
            )
        ]

    def __str__(self):
        return " > ".join((self.project.name, self.objective.name))

    def status(self):
        for level in reversed(Level.objects.all()):
            if ProjectObjectiveCondition.objects.filter(
                projectobjective=self, condition__level=level, done=True
            ):
                return level

        return self.get_if_not_started_display()

    def status_slug(self):
        return slugify(self.status())

    def name(self):
        return self.objective.name

    class Meta:
        ordering = ["project", "objective"]


class ProjectObjectiveCondition(models.Model):

    projectobjective = models.ForeignKey(ProjectObjective, on_delete=models.CASCADE)
    condition = models.ForeignKey(Condition, on_delete=models.CASCADE)
    done = models.BooleanField(default=False)

    def level(self):
        return self.condition.level

    def __str__(self):
        return " > ".join((self.projectobjective.__str__(), self.condition.name))

    def name(self):
        return self.condition.name

    class Meta:
        ordering = ["condition"]

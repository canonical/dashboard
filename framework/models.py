from django.db import models


class ProjectStatus(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Level(models.Model):
    name = models.CharField(max_length=200)
    value = models.SmallIntegerField()

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["value"]


class WorkCycle(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

    def save(self, **kwargs):
        # when a new WorkCycle is added propagate it to all existing LevelCommitments

        from projects.models import (
            ProjectObjective,
            LevelCommitment,
        )  # avoids circular import

        super().save(**kwargs)

        # get all ProjectObjectives
        projectobjectives = ProjectObjective.objects.all()

        for project_objective in projectobjectives:

            for level in Level.objects.all():
                LevelCommitment.objects.get_or_create(
                    work_cycle=self, project_objective=project_objective, level=level
                )


class ObjectiveGroup(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Objective(models.Model):
    # a dimension in which quality can be measured

    name = models.CharField(max_length=100)
    group = models.ForeignKey("ObjectiveGroup", on_delete=models.CASCADE)
    weight = models.SmallIntegerField()

    def __str__(self):
        return self.name

    def save(self, **kwargs):
        # when a new Objective is added propagate it to all existing Projects

        from projects.models import ProjectObjective, Project  # avoids circular import

        super().save(**kwargs)

        for project in Project.objects.exclude(objectives=self):
            ProjectObjective(project=project, objective=self).save()

    class Meta:
        ordering = ["group", "name"]


class Condition(models.Model):

    # e.g. "All new content is created according to Diátaxis principles"
    name = models.CharField(max_length=100)
    objective = models.ForeignKey(Objective, on_delete=models.CASCADE)
    level = models.ForeignKey(Level, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    def save(self, **kwargs):
        # when a new Condition is added propagate it to all existing ProjectObjectives

        from projects.models import (
            ProjectObjective,
            ProjectObjectiveCondition,
        )  # avoids circular import

        super().save(**kwargs)

        projectobjectives = ProjectObjective.objects.filter(objective=self.objective)

        for projectobjective in projectobjectives:
            ProjectObjectiveCondition.objects.get_or_create(
                projectobjective=projectobjective, condition=self
            )

    class Meta:
        ordering = ["level"]

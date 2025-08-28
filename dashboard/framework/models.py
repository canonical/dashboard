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
    timestamp = models.DateField()

    def __str__(self):
        return self.name

    def save(self, **kwargs):
        # when a new WorkCycle is added, create a LevelCommitment for it

        # to do: if Conditions with new Levels are added for an Objective,
        # we also need to propagate the LevelCommitment objects

        from projects.models import (
            ProjectObjective,
            LevelCommitment,
            Project,
            QI,
        )  # avoids circular import

        super().save(**kwargs)

        # get all ProjectObjectives
        projectobjectives = ProjectObjective.objects.all()

        for level in Level.objects.all():
            for project_objective in projectobjectives.filter(
                objective__condition__level=level
            ):
                l = LevelCommitment.objects.get_or_create(
                    work_cycle=self,
                    project=project_objective.project,
                    objective=project_objective.objective,
                    level=level,
                )

        # make sure there's a QI object for this WorkCycle for each Project
        for project in Project.objects.all():
            QI.objects.get_or_create(workcycle=self, project=project)

    class Meta:
        ordering = ["timestamp"]


class ObjectiveGroup(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Objective(models.Model):
    # a dimension in which quality can be measured

    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    group = models.ForeignKey("ObjectiveGroup", on_delete=models.CASCADE)
    weight = models.SmallIntegerField()

    def __str__(self):
        return self.name

    def save(self, **kwargs):
        # when a new Objective is added propagate it to all existing Projects

        from projects.models import ProjectObjective, Project, LevelCommitment  # avoids circular import

        super().save(**kwargs)


        # go over the Projects (but not any already with a relation to this objective, because that's unnecessary)
        for project in Project.objects.exclude(objectives=self):
            ProjectObjective(project=project, objective=self).save()

        levels = self.condition_set.all()

        for level in Level.objects.all():
            for project in Project.objects.all():
                for work_cycle in WorkCycle.objects.all():
                    l = LevelCommitment.objects.get_or_create(
                        work_cycle=work_cycle,
                        project=project,
                        objective=self,
                        level=level,
                    )


    class Meta:
        ordering = ["group", "name"]


class Condition(models.Model):

    # e.g. "All new content is created according to Diátaxis principles"
    name = models.TextField(max_length=250)
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
                project=projectobjective.project,
                objective=projectobjective.objective,
                condition=self,
            )

    class Meta:
        ordering = ["level"]

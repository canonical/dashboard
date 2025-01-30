from django.contrib import admin

import nested_admin

from .models import (
    ProjectGroup,
    Project,
    ProjectObjective,
    Condition,
    ProjectObjectiveCondition,
    LevelCommitment,
)


class LevelCommitmentInline(admin.TabularInline):
    model = LevelCommitment
    max_num = 0
    can_delete = False
    readonly_fields = ["work_cycle", "level"]
    classes = ["collapse"]


# ---- ProjectAdmin


class ProjectObjectiveConditionInline(admin.TabularInline):
    model = ProjectObjectiveCondition
    max_num = 0
    can_delete = False
    readonly_fields = ["name", "level"]
    exclude = ["condition"]


class ProjectObjectiveInline(admin.TabularInline):
    model = ProjectObjective
    inlines = [ProjectObjectiveConditionInline]
    max_num = 0
    can_delete = False
    readonly_fields = ["name", "status"]
    exclude = ["if_not_started", "objective"]


@admin.register(ProjectObjective)
class ProjectObjectiveAdmin(admin.ModelAdmin):
    inlines = [ProjectObjectiveConditionInline, LevelCommitmentInline]
    readonly_fields = ["project", "objective", "status"]

    fieldsets = (
        (
            None,
            {
                "fields": (
                    ("if_not_started", "status"),
                    ("project", "objective"),
                ),
            },
        ),
    )


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    inlines = [ProjectObjectiveInline]
    list_display = ["name", "owner", "driver", "last_review", "last_review_status"]

    fieldsets = (
        (
            None,
            {
                "fields": (
                    ("name", "group"),
                    ("owner", "driver"),
                    ("last_review", "last_review_status"),
                )
            },
        ),
    )


admin.site.register(ProjectGroup)

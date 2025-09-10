from django.contrib import admin
from django import forms

from .models import (
    ProjectGroup,
    Project,
    ProjectObjective,
    ProjectObjectiveCondition,
    Commitment,
    QI,
)

from framework.models import WorkCycle


class ProjectObjectiveConditionInline(admin.TabularInline):
    model = ProjectObjectiveCondition
    can_delete = False
    readonly_fields = ["condition"]
    exclude = ["condition", "objective", "level"]

    def has_add_permission(self, request, obj):
        return False

    def has_delete_permission(self, request, obj):
        return False


class CommitmentInline(admin.TabularInline):
    model = Commitment
    max_num = 0
    can_delete = False
    fields = ["committed"]
    classes = ["collapse"]

    def change_view(self, request, object_id, form_url="", extra_context=None):
        extra_context = extra_context or {}
        extra_context["work_cycles"] = WorkCycle.objects.all()
        return super().change_view(
            request,
            object_id,
            form_url,
            extra_context=extra_context,
        )

    def has_add_permission(self, request, obj):
        return False

    def has_delete_permission(self, request, obj):
        return False


class ProjectObjectiveInline(admin.TabularInline):
    model = ProjectObjective
    max_num = 0
    can_delete = False
    fields = ("name", "unstarted_reason")
    readonly_fields = ["name"]
    exclude = ["objective", "description", "status"]

    def has_add_permission(self, request, obj):
        return False

    def has_delete_permission(self, request, obj):
        return False


@admin.register(ProjectObjective)
class ProjectObjectiveAdmin(admin.ModelAdmin):
    readonly_fields = ["project", "objective", "status"]
    list_filter = ["project", "objective", "unstarted_reason"]

    fieldsets = (
        (
            None,
            {
                "fields": (
                    ("unstarted_reason", "status"),
                    ("project", "objective"),
                ),
            },
        ),
    )

    def change_view(self, request, object_id, form_url="", extra_context=None):
        extra_context = extra_context or {}
        extra_context["test"] = "success!"
        return super().change_view(
            request,
            object_id,
            form_url,
            extra_context=extra_context,
        )


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    inlines = [
        ProjectObjectiveInline,
    ]
    list_display = [
        "name",
        "owner",
        "driver",
        "last_review",
        "agreement_status",
        "last_review_status",
    ]
    save_on_top = True

    fieldsets = (
        (
            None,
            {
                "fields": (
                    ("name", "group"),
                    ("owner", "driver"),
                    ("agreement_status"),
                    ("last_review", "last_review_status"),
                )
            },
        ),
    )


@admin.register(Commitment)
class CommitmentAdmin(admin.ModelAdmin):
    list_filter = ["work_cycle", "project", "objective", "level", "committed"]


@admin.register(ProjectObjectiveCondition)
class ProjectObjectiveConditionAdmin(admin.ModelAdmin):
    list_filter = ["project", "objective", "condition", "done"]


admin.site.register(ProjectGroup)
admin.site.register(QI)

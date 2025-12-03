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
                    ("name", "url", "group"),
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
    list_filter = ["project", "objective", "condition", "status"]


class FilterFieldOrderByName(admin.filters.RelatedFieldListFilter):
    def field_choices(self, field, request, model_admin):
        objects_by_name = field.remote_field.model._default_manager.order_by("name")
        return [(obj.pk, str(obj)) for obj in objects_by_name]


@admin.register(QI)
class QIAdmin(admin.ModelAdmin):
    list_filter = [("project", FilterFieldOrderByName)]


admin.site.register(ProjectGroup)

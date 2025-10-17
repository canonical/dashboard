from django.contrib import admin

from .models import (
    Level,
    Reason,
    ProjectStatus,
    AgreementStatus,
    WorkCycle,
    ObjectiveGroup,
    Objective,
    Condition,
)


class ConditionAdmin(admin.ModelAdmin):
    list_display = ["name", "objective", "level"]
    list_editable = ["objective", "level"]

class ConditionInline(admin.TabularInline):
    model = Condition
    extra = 1


class ObjectiveAdmin(admin.ModelAdmin):
    inlines = [ConditionInline]
    list_display = ["name", "group", "weight"]
    list_editable = ["group", "weight"]


class WorkCycleAdmin(admin.ModelAdmin):
    list_display = ["name", "timestamp", "is_current"]
    list_editable = ["timestamp", "is_current"]


admin.site.register(Level)
admin.site.register(Reason)
admin.site.register(ProjectStatus)
admin.site.register(AgreementStatus)
admin.site.register(WorkCycle, WorkCycleAdmin)
admin.site.register(ObjectiveGroup)
admin.site.register(Condition, ConditionAdmin)
admin.site.register(Objective, ObjectiveAdmin)

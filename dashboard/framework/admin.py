from django.contrib import admin

from .models import (
    Level,
    Reason,
    ProjectStatus,
    WorkCycle,
    ObjectiveGroup,
    Objective,
    Condition,
)


class ConditionInline(admin.TabularInline):
    model = Condition
    extra = 1


class ObjectiveAdmin(admin.ModelAdmin):
    inlines = [ConditionInline]
    list_display = ["name", "group", "weight"]
    list_editable = ["group", "weight"]


class WorkCycleAdmin(admin.ModelAdmin):
    model = WorkCycle
    list_display = ["name", "timestamp"]
    list_editable = ["timestamp"]


admin.site.register(Level)
admin.site.register(Reason)
admin.site.register(ProjectStatus)
admin.site.register(WorkCycle, WorkCycleAdmin)
admin.site.register(ObjectiveGroup)
# admin.site.register(Condition)
admin.site.register(Objective, ObjectiveAdmin)

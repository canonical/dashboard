from django.contrib import admin

from .models import (
    Level,
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


admin.site.register(Level)
admin.site.register(ProjectStatus)
admin.site.register(WorkCycle)
admin.site.register(ObjectiveGroup)
admin.site.register(Condition)
admin.site.register(Objective, ObjectiveAdmin)

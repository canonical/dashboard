from django.db import migrations


def populate_status(apps, schema_editor):
    ProjectObjectiveCondition = apps.get_model("projects", "ProjectObjectiveCondition")
    for poc in ProjectObjectiveCondition.objects.all():
        if poc.done:
            poc.status = "DO"
        elif poc.not_applicable:
            poc.status = "NA"
        elif poc.candidate:
            poc.status = "CA"
        poc.save()


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0014_projectobjectivecondition_status'),
    ]

    operations = [
        migrations.RunPython(populate_status),
    ]

# Generated by Django 4.2.11 on 2024-03-14 08:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('calendarapp', '0004_project_task'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='project',
            name='end_date',
        ),
    ]
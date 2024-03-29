# Generated by Django 4.2.11 on 2024-03-19 04:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('calendarapp', '0006_projecttemplate'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='template',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='calendarapp.projecttemplate'),
        ),
        migrations.AddField(
            model_name='task',
            name='days_prior',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='task',
            name='duration',
            field=models.IntegerField(),
        ),
    ]

# Generated by Django 4.2.1 on 2023-05-31 16:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='class',
            name='class_leader',
        ),
        migrations.AddField(
            model_name='class',
            name='class_leader_id',
            field=models.CharField(blank=True, default=None, max_length=20, null=True, unique=True),
        ),
    ]
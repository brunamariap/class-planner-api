from django.db import models


class Teacher(models.Model):
    class Meta:
        db_table = 'teacher'

    registration = models.CharField(max_length=8)
    name = models.CharField(max_length=200)
    avatar = models.ImageField(null=True)
    department = models.CharField(max_length=30)

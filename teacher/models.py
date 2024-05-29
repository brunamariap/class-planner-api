from django.db import models


class Teacher(models.Model):
    class Meta:
        db_table = 'teacher'

    registration = models.CharField(max_length=14, unique=True)
    name = models.CharField(max_length=200)
    avatar = models.CharField(max_length=200,null=True)
    department = models.CharField(max_length=30)
    email = models.EmailField(max_length=254)

from django.db import models


class Teacher(models.Model):
    registration = models.CharField(max_length=8)
    name = models.CharField(max_length=200)
    avatar = models.ImageField()
    departament = models.CharField(max_length=30)
from django.db import models
from course.models import Class, Discipline


class Student(models.Model):
    registration = models.CharField(max_length=32)
    name = models.CharField(max_length=200)
    avatar = models.ImageField()
    class_id = models.ForeignKey(Class, on_delete=models.DO_NOTHING)


class StudentAlert(models.Model):
    discipline = models.ForeignKey(Discipline, on_delete=models.DO_NOTHING)
    student = models.ForeignKey(Student, on_delete=models.DO_NOTHING)
    created_at = models.DateTimeField(auto_now_add=True)
    reason = models.TextField(max_length=200, blank=True, null=True)
    

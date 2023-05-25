from django.db import models
from student.models import Student


class Course(models.Model):
    name = models.CharField(max_length=30)
    degree = models.CharField(max_length=20)
    course_load = models.IntegerField()
    byname = models.CharField(max_length=10)  


class Discipline(models.Model):
    name = models.CharField(max_length=30)
    code = models.CharField(max_length=15)
    workload_in_clock = models.IntegerField()
    workload_in_class = models.IntegerField()
    is_optional = models.BooleanField()
    courses = models.ManyToManyField(Course)


class Class(models.Model):
    class Shift(models.TextChoices):
        MATUTINO = 'Manhã'
        VESPERTINO = 'Tarde'
        NOTURNO = 'Noite'
    
    class_leader = models.ForeignKey(Student, on_delete=models.DO_NOTHING, blank=True, null=True)
    course = models.ForeignKey(Course, on_delete=models.DO_NOTHING)
    reference_period = models.IntegerField()
    shift = models.CharField(max_length=10, choices=Shift.choices)


class Schedule(models.Model):
    discipline = models.ForeignKey(Discipline, on_delete=models.DO_NOTHING)
    quantity = models.IntegerField()
    weekday = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    schedule_class = models.ForeignKey(Class, on_delete=models.CASCADE)


class ClassCanceled(models.Model):
    schedule = models.ForeignKey(Schedule, on_delete=models.DO_NOTHING)
    canceled_date = models.DateField()
    reason = models.TextField(max_length=200, blank=True, null=True)
    is_avaible = models.BooleanField()

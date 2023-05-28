from django.db import models
from course.models import Class, Discipline


class Student(models.Model):
    class Meta:
        db_table = 'student'

    registration = models.CharField(max_length=32)
    name = models.CharField(max_length=200)
    avatar = models.ImageField(null=True)
    class_id = models.ForeignKey(Class, on_delete=models.DO_NOTHING, db_column='class_id')
    disciplines = models.ManyToManyField(Discipline) 


""" class StudentDisciplines(models.Model):
    student_id = models.ForeignKey(Student, on_delete=models.CASCADE, db_column='student_id')
    discipline_id = models.ForeignKey(Discipline, on_delete=models.CASCADE, db_column='discipline_id') """


class StudentAlert(models.Model):
    class Meta:
        db_table = 'student_alert'
    
    discipline_id = models.ForeignKey(Discipline, on_delete=models.DO_NOTHING, db_column='discipline_id')
    student_id = models.ForeignKey(Student, on_delete=models.DO_NOTHING, db_column='student_id')
    created_at = models.DateTimeField(auto_now_add=True)
    reason = models.TextField(max_length=200, blank=True, null=True)
    

from rest_framework import serializers
from course.api.serializers import ClassSerializer, DisciplineSerializer

from ..models import Student, StudentAlert


class StudentSerializer(serializers.ModelSerializer):
    student_class = ClassSerializer()

    class Meta:
        model = Student
        fields = ['id', 'registration', 'avatar','student_class']

class StudentAlertSerializer(serializers.ModelSerializer):
    discipline = DisciplineSerializer()
    student = StudentSerializer()

    class Meta:
        model = StudentAlert
        fields = ['id', 'discipline', 'student','created_at','reason']
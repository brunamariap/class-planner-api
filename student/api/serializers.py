from rest_framework import serializers
from course.api.serializers import ClassSerializer, DisciplineSerializer
from course.models import Discipline
from ..models import Student, StudentAlert


class StudentSerializer(serializers.ModelSerializer):
    disciplines = serializers.SlugRelatedField(queryset=Discipline.objects.all(), slug_field='code', required=False, many=True)
    class Meta:
        model = Student
        fields = ['id', 'name', 'registration', 'avatar','class_id', 'email', 'disciplines']


class ClassStudentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ['id', 'name', 'registration', 'avatar', 'disciplines']


class StudentAlertSerializer(serializers.ModelSerializer):
    discipline_id = DisciplineSerializer(read_only=True)
    student_id = StudentSerializer(read_only=True)

    class Meta:
        model = StudentAlert
        fields = ['id', 'discipline_id', 'student_id', 'created_at', 'reason']
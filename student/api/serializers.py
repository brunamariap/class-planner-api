from rest_framework import serializers
from course.api.serializers import ClassSerializer, DisciplineSerializer
from course.models import Discipline
from ..models import Student, StudentAlert


class StudentSerializer(serializers.ModelSerializer):
    disciplines = serializers.SlugRelatedField(queryset=Discipline.objects.all(), slug_field='code', required=False, many=True)
    class Meta:
        model = Student
        fields = ['id', 'name', 'registration', 'avatar','class_id', 'disciplines']

class StudentAlertSerializer(serializers.ModelSerializer):
    discipline = DisciplineSerializer()
    student = StudentSerializer()

    class Meta:
        model = StudentAlert
        fields = ['id', 'discipline', 'student','created_at','reason']
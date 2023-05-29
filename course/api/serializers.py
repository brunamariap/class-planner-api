from rest_framework import serializers
from ..models import Course, Discipline, Class, Schedule, Teach, CourseDiscipline


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 'name', 'degree', 'course_load', 'byname']


class DisciplineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Discipline
        fields = ['id', 'name', 'code', 'workload_in_clock', 'workload_in_class', 'is_optional']


class TeachSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teach
        fields = ['id', 'teacher_id', 'discipline_id', 'class_id']


class CourseDisciplineSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseDiscipline
        fields = ['id', 'discipline_id', 'course_id', 'period']


class ClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = Class
        fields = ['id', 'course_id', 'reference_period', 'shift', 'class_leader']


class ScheduleSerializer(serializers.ModelSerializer):
    discipline = CourseSerializer(read_only=True)
    schedule_class = CourseSerializer(read_only=True)
    class Meta:
        model = Schedule
        fields = ['id', 'quantity', 'start_time', 'end_time', 'discipline', 'schedule_class']
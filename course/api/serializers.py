from rest_framework import serializers
from ..models import Course, Discipline, Class, Schedule


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 'name', 'degree', 'course_load', 'byname']


class DisciplineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Discipline
        fields = ['id', 'name', 'code', 'workload_in_clock', 'workload_in_class', 'is_optional']


class ClassSerializer(serializers.ModelSerializer):
    # course_id = CourseSerializer(read_only=True)

    class Meta:
        model = Class
        fields = ['id', 'course_id', 'reference_period', 'shift']


class ScheduleSerializer(serializers.ModelSerializer):
    discipline = CourseSerializer(read_only=True)
    schedule_class = CourseSerializer(read_only=True)
    class Meta:
        model = Schedule
        fields = ['id', 'quantity', 'start_time', 'end_time', 'discipline', 'schedule_class']
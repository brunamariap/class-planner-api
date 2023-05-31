from rest_framework import serializers
from ..models import Course, Discipline, Class, Schedule, Teach, CourseDiscipline, TemporaryClass, ClassCanceled

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 'name', 'degree', 'course_load', 'byname']


class CourseDisciplineSerializer(serializers.ModelSerializer):
    # course_id = CourseSerializer()
    class Meta:
        model = CourseDiscipline
        fields = ['id', 'course_id']


class DisciplineSerializer(serializers.ModelSerializer):
    course_period = serializers.SerializerMethodField('show_course_period')

    class Meta:
        model = Discipline
        fields = ['id', 'name', 'code', 'workload_in_clock',
                  'workload_in_class', 'is_optional', 'course_period']

    def show_course_period(self, instance):
        course_discipline_objects = CourseDiscipline.objects.filter(
            discipline_id=instance.id)

        course_period = []
        for object in course_discipline_objects.values():
            course_period.extend(
                [{'course_id': object['course_id_id'], 'period': object['period']}])

        return course_period


class TeachSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teach
        fields = ['id', 'teacher_id', 'discipline_id', 'class_id']


class DisciplineWithTeachSerializer(serializers.ModelSerializer):
    course_period = serializers.SerializerMethodField('show_course_period')
    taught_by = serializers.SerializerMethodField('show_taught_by')

    class Meta:
        model = Discipline
        fields = ['id', 'name', 'code', 'workload_in_clock', 'workload_in_class', 'is_optional', 'course_period', 'taught_by']

    def show_course_period(self, instance):
        course_discipline_objects = CourseDiscipline.objects.filter(
            discipline_id=instance.id)

        course_period = []
        for object in course_discipline_objects.values():
            course_period.extend(
                [{'course_id': object['course_id_id'], 'period': object['period']}])

        return course_period
    
    def show_taught_by(self, instance):
        
        if instance:
            data = instance.teach_set
            serializer = TeachSerializer(data, many=True)

            return serializer.data
    
        return None


class ClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = Class
        fields = ['id', 'course_id',
                  'reference_period', 'shift', 'class_leader']


class ScheduleSerializer(serializers.ModelSerializer):
    discipline = CourseSerializer(read_only=True)
    schedule_class = ClassSerializer(read_only=True)

    class Meta:
        model = Schedule
        fields = ['id', 'quantity', 'weekday', 'start_time','end_time', 'discipline_id', 'class_id', 'discipline', 'schedule_class']

class TemporaryClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = TemporaryClass
        fields = '__all__'

class ClassCanceledSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassCanceled
        fields = ['id','schedule_id', 'canceled_date','reason', 'is_available', 'quantity_available', 'teacher_ids']
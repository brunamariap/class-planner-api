from rest_framework import serializers
from ..models import Course, Discipline, Class, Schedule, Teach, CourseDiscipline, TemporaryClass, ClassCanceled

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 'name', 'degree', 'course_load', 'byname']


class CourseDisciplineSerializer(serializers.ModelSerializer):
    # course_id = CourseSerializer()
    class Meta:
        model = Discipline
        fields = ['id', 'name', 'code', 'workload_in_clock', 'workload_in_class', 'is_optional']


class CourseDisciplinePeriodSerializer(serializers.ModelSerializer):
    #discipline = serializers.SerializerMethodField('show_discipline')
    discipline_id = CourseDisciplineSerializer(read_only=True)

    class Meta:
        model = CourseDiscipline
        fields = ['discipline_id', 'period']

    def show_discipline(self, instance):
        if instance:  
            discipline_obj = Discipline.objects.get(id=instance.discipline_id)
            print(discipline_obj)
            #discipline = CourseDisciplineSerializer(discipline_obj)
            #print(discipline)
            return {"discipline": discipline_obj}
        

class CourseClassesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Class
        fields = ['id', 'reference_period', 'shift', 'class_leader_id']


class DisciplineSerializer(serializers.ModelSerializer):
    course_period = serializers.SerializerMethodField('show_course_period')

    class Meta:
        model = Discipline
        fields = ['id', 'name', 'code', 'workload_in_clock', 'workload_in_class', 'is_optional', 'course_period']

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
        fields = ['id', 'course_id', 'reference_period', 'shift', 'class_leader_id']


class TemporaryClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = TemporaryClass
        fields = ['id', 'class_canceled_id', 'quantity', 'teacher_id', 'discipline_id']


class ClassCanceledSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassCanceled
        fields = ['id','schedule_id', 'canceled_date','reason', 'is_available', 'quantity_available', 'teacher_ids']

class ScheduleSerializer(serializers.ModelSerializer):
    discipline = CourseSerializer(read_only=True)
    schedule_class = ClassSerializer(read_only=True)

    temporary_class_id = serializers.SerializerMethodField('show_temporary_class_id')
    canceled_class = serializers.SerializerMethodField('show_canceled_class')
    class_to_replace = serializers.SerializerMethodField('show_class_to_replace') 

    class Meta:
        model = Schedule
        fields = ['id', 'quantity', 'weekday', 'start_time','end_time', 'discipline_id', 'class_id', 'discipline', 'schedule_class', 'canceled_class', 'class_to_replace', 'temporary_class_id']

    def without_results(self, instance):
        return None

    def show_temporary_class_id(self, instance):
        try:
            return instance.temporary_class_id['id']
        except:
            return None

    def show_canceled_class(self, instance):
        try:
            canceled_schedule = ClassCanceled.objects.get(schedule_id=instance.id)

            if (canceled_schedule):
                serializer = ClassCanceledSerializer(canceled_schedule)

                return serializer.data
        except:
            return None
    
    def show_class_to_replace(self, instance):
        
        try:
            canceled_schedule = ClassCanceled.objects.get(schedule_id=instance.id)
        
            if not (canceled_schedule):
                return None
            
            classes_to_replace = TemporaryClass.objects.filter(class_canceled_id=canceled_schedule)
            
            if (classes_to_replace):
                serializer = TemporaryClassSerializer(classes_to_replace, many=True)

                return serializer.data
    
        except:
            return None
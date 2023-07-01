from rest_framework import serializers
from ..models import Course, Discipline, Class, Schedule, Teach, CourseDiscipline, TemporaryClass, ClassCanceled
from datetime import datetime, timedelta, date

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 'name', 'degree', 'course_load', 'byname']


class CourseDisciplineSerializer(serializers.ModelSerializer):
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
            print('instancia: ', instance.discipline_id)
            """ discipline_obj = Discipline.objects.get(id=instance.discipline_id) """
            #print(discipline_obj)
            discipline = Discipline.objects.get(id=instance.discipline_id.id)
            serializer =  CourseDisciplineSerializer(data=discipline)
            print(serializer)
            serializer.is_valid()
            print('data',serializer.data)
            #discipline = CourseDisciplineSerializer(discipline_obj)
            #print(discipline)
            return serializer.data
        

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
    teacher = serializers.SerializerMethodField('show_teacher', required=False)

    def show_teacher(self, instance):
        from teacher.api.serializers import TeacherSerializer

        try:
            serializer = TeacherSerializer(instance.teacher_id)

            return serializer.data
        except:
            return None
    class Meta:
        model = Teach
        fields = ['id', 'teacher_id', 'teacher', 'discipline_id', 'class_id']


class DisciplineWithTeachSerializer(serializers.ModelSerializer):
    course_period = serializers.SerializerMethodField('show_course_period')
    taught_by = serializers.SerializerMethodField('show_taught_by')

    class Meta:
        model = Discipline
        fields = ['id', 'name', 'code', 'workload_in_clock', 'workload_in_class', 'is_optional', 'course_period', 'taught_by']

    def show_course_period(self, instance):
        course_discipline_objects = CourseDiscipline.objects.filter(
            discipline_id=instance['id'])
        
        course_period = []
        for object in course_discipline_objects.values():
            course_period.extend(
                [{'course_id': object['course_id_id'], 'period': object['period']}])

        return course_period
    
    def show_taught_by(self, instance):
            
        if instance:
            data = Teach.objects.filter(discipline_id=instance['id'], class_id=instance['class_id'])
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
    discipline = serializers.SerializerMethodField('show_discipline', required=False)
    schedule_class = serializers.SerializerMethodField('show_class', required=False)

    canceled_class = serializers.SerializerMethodField('show_canceled_classes')
    class_to_replace = serializers.SerializerMethodField('show_classes_to_replace') 
    class_date = serializers.SerializerMethodField('show_class_date')

    class Meta:
        model = Schedule
        fields = ['id', 'quantity', 'weekday', 'start_time','end_time', 'class_id', 'schedule_class', 'discipline_id', 'discipline', 'canceled_class', 'class_to_replace', 'class_date']

    def show_discipline(self, instance):
        serializer = DisciplineWithTeachSerializer(instance.discipline_id)

        return serializer.data 
    
    def show_class(self, instance):
        serializer = ClassSerializer(instance.class_id)

        return serializer.data 
    
    def without_results(self, instance):
        return None

    def show_class_date(self, instance):
        try:
            return instance.date
        except:
            return None

    def show_canceled_classes(self, instance):
        canceled_schedules = ClassCanceled.objects.filter(schedule_id=instance.id)
        
        reference_date = datetime.strptime(self.context['request'].query_params['date'], '%d/%m/%Y').date() if 'date' in self.context['request'].query_params else date.today()

        
        if len(canceled_schedules) > 0:
            week_canceled_schedules = []

            for schedule in canceled_schedules.values():
                current_day = instance.date if hasattr(instance, 'date') else reference_date
                weekday = current_day.weekday()
                next_monday = current_day - timedelta(days=weekday+1)
                weekdates = [next_monday + timedelta(days=x) for x in range(7)]
                
                if schedule['canceled_date'] in weekdates:
                    schedule['schedule_id'] = schedule['schedule_id_id']
                    week_canceled_schedules.append(schedule)
                
            serializer = ClassCanceledSerializer(data=week_canceled_schedules, many=True)
            serializer.is_valid()

            if len(serializer.data) > 0:
                return serializer.data[0]

        return None
    
    def show_classes_to_replace(self, instance):
        canceled_schedules = ClassCanceled.objects.filter(schedule_id=instance.id)
        
        if len(canceled_schedules) < 1:
            return None
        
        reference_date = datetime.strptime(self.context['request'].query_params['date'], '%d/%m/%Y').date() if 'date' in self.context['request'].query_params else date.today()
        classes_to_replace = TemporaryClass.objects.filter(class_canceled_id__id__in=canceled_schedules)
        
        week_replaced_classes = []

        for schedule in classes_to_replace.values():
            current_day = instance.date if hasattr(instance, 'date') else reference_date
            weekday = current_day.weekday()
            sunday = current_day - timedelta(days=weekday+1)
            weekdates = [sunday + timedelta(days=x) for x in range(7)]
            
            canceled_class = ClassCanceled.objects.get(id=schedule['class_canceled_id_id'])

            if canceled_class.canceled_date in weekdates:
                schedule['class_canceled_id'] = schedule['class_canceled_id_id']
                schedule['teacher_id'] = schedule['teacher_id_id']
                schedule['discipline_id'] = schedule['discipline_id_id']

                week_replaced_classes.append(schedule)
        
        serializer = TemporaryClassSerializer(data=week_replaced_classes, many=True)
        serializer.is_valid()

        if len(serializer.data) == 0:
            return None

        return serializer.data

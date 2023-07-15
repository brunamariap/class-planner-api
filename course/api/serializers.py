from rest_framework import serializers
from ..models import Course, Discipline, Class, Schedule, Teach, CourseDiscipline, TemporaryClass, ClassCanceled
from datetime import datetime, timedelta, date
from teacher.api.serializers import TeacherSerializer
from teacher.models import Teacher
class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 'name', 'degree', 'course_load', 'byname']


class CourseDisciplineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Discipline
        fields = ['id', 'name', 'code', 'workload_in_class', 'workload_in_clock', 'is_optional']


class CourseDisciplinePeriodSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseDiscipline
        fields = ['id', 'discipline', 'course_degree', 'period']

    discipline = serializers.SerializerMethodField('show_discipline')
    course_degree = serializers.SerializerMethodField('show_course_degree')

    def show_course_degree(self, instance):
        course = Course.objects.get(id=instance.course_id.id)
        degree = course.degree

        return degree

    def show_discipline(self, instance):
        discipline = Discipline.objects.get(id=instance.discipline_id.id)
        serializer =  CourseDisciplineSerializer(discipline)
    
        return serializer.data 
        

class CourseClassesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Class
        fields = ['id', 'reference_period', 'shift', 'class_leader_id']


class DisciplineSerializer(serializers.ModelSerializer):
    course = serializers.SerializerMethodField('show_course_period')

    class Meta:
        model = Discipline
        fields = ['id', 'name', 'code', 'workload_in_clock', 'workload_in_class', 'is_optional', 'course']

    def show_course_period(self, instance):
        course_discipline_objects = CourseDiscipline.objects.filter(
            discipline_id=instance.id)
        
        course_period = []
        for object in course_discipline_objects.values():
            course = Course.objects.get(id=object['course_id_id'])
            serializer = CourseSerializer(course)
            
            formattedCourse = serializer.data
            formattedCourse.update({'period': object['period']})

            course_period.append(formattedCourse)

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
    course = serializers.SerializerMethodField('show_course_period')
    taught_by = serializers.SerializerMethodField('show_taught_by')

    class Meta:
        model = Discipline
        fields = ['id', 'name', 'code', 'workload_in_clock', 'workload_in_class', 'is_optional', 'course', 'taught_by']

    def show_course_period(self, instance):
        try:
            course_discipline_objects = CourseDiscipline.objects.filter(
            discipline_id=instance.id)
        
            course_period = []
            for object in course_discipline_objects.values():
                course = Course.objects.get(id=object['course_id_id'])
                serializer = CourseSerializer(course)
                
                formattedCourse = serializer.data
                formattedCourse.update({'period': object['period']})

                course_period.append(formattedCourse)

            return course_period
        except:
            try:
                course_discipline_objects = CourseDiscipline.objects.filter(
                discipline_id=instance['id'])
            
                course_period = []
                for object in course_discipline_objects.values():
                    course = Course.objects.get(id=object['course_id_id'])
                    serializer = CourseSerializer(course)
                    
                    formattedCourse = serializer.data
                    formattedCourse.update({'period': object['period']})

                    course_period.append(formattedCourse)

                return course_period
            except:
                return None
    
    def show_taught_by(self, instance):
        if instance:
            teach = Teach.objects.filter(discipline_id=instance['id'], class_id=instance['class_id'])
            teachers = Teacher.objects.filter(id__in=teach.values_list('teacher_id', flat=True))
            
            data = TeacherSerializer(teachers, many=True)

            return data.data
    
        return None


class ClassSerializer(serializers.ModelSerializer):
    course = serializers.SerializerMethodField('show_course')
    class Meta:
        model = Class
        fields = ['id', 'course_id', 'course', 'reference_period', 'shift', 'class_leader_id', ]

    def show_course(self, instance):
        course = Course.objects.get(id=instance.course_id.id)
        serializer = CourseSerializer(course)
        return serializer.data


class TemporaryClassSerializer(serializers.ModelSerializer):
    discipline = serializers.SerializerMethodField('show_discipline')
    teacher = serializers.SerializerMethodField('show_teacher')

    class Meta:
        model = TemporaryClass
        fields = ['id', 'class_canceled_id', 'quantity', 'teacher_id', 'teacher', 'discipline_id', 'discipline']

    def show_discipline(self, instance):
        discipline = Discipline.objects.get(id=instance['discipline_id'].id)

        serializer = DisciplineSerializer(discipline)

        return serializer.data
    
    def show_teacher(self, instance):
        discipline = Teacher.objects.get(id=instance['teacher_id'].id)

        serializer = TeacherSerializer(discipline)

        return serializer.data


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
        fields = ['id', 'quantity', 'weekday', 'start_time','end_time', 'class_id', 'schedule_class','discipline_id', 'discipline', 'canceled_class', 'class_to_replace', 'class_date']

    def show_discipline(self, instance):
        discipline = Discipline.objects.filter(id=instance.discipline_id.id)
        
        data = []
        for i in discipline.values():
            i['class_id'] = instance.class_id
            data.append(i)

        serializer = DisciplineWithTeachSerializer(data[0])

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
        
        reference_date = datetime.strptime(self.context['request'].query_params['date'], '%d/%m/%Y').date() if 'date' in self.context['request'].query_params else date.today()

        canceled_schedules = ClassCanceled.objects.filter(schedule_id=instance.id, canceled_date=reference_date)
        
        if len(canceled_schedules) < 1:
            return None

        classes_to_replace = TemporaryClass.objects.filter(class_canceled_id__id__in=canceled_schedules)
        
        if self.context['student_id']:
            print('entrei ne')
            from student.api.serializers import StudentSerializer
            from student.models import Student

            try:
                student = Student.objects.get(id=self.context['student_id'])
                student_values = StudentSerializer(student)
                student_disciplines = Discipline.objects.filter(code__in=student_values.data['disciplines']).values_list('code', flat=True)

                wasReplaced = TemporaryClass.objects.get(class_canceled_id=canceled_schedules.first().id)
                
                if wasReplaced.discipline_id.code not in student_disciplines:
                    return None 
            except:
                pass

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

        return serializer.data[0]

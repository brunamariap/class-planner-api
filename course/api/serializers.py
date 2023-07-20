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
        serializer = CourseDisciplineSerializer(discipline)

        return serializer.data
    

class DisciplineSerializer(serializers.ModelSerializer):
    course = serializers.SerializerMethodField('show_course_period')

    class Meta:
        model = Discipline
        fields = ['id', 'name', 'code', 'workload_in_clock',
                  'workload_in_class', 'is_optional', 'course']

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


class TeacherDisciplineSerializer(serializers.ModelSerializer):
    course = serializers.SerializerMethodField('show_course_period')
    discipline = serializers.SerializerMethodField('show_discipline')
    teach_class = serializers.SerializerMethodField('show_class')

    class Meta:
        model = Teach
        fields = ['id', 'discipline', 'course', 'teach_class']

    def show_course_period(self, instance, *args, **kwargs):
        try:
            class_id = Class.objects.get(id=instance.class_id.id)
            course_discipline_object = CourseDiscipline.objects.get(
                course_id=class_id.course_id, discipline_id=instance.discipline_id)
            serializer = CourseSerializer(class_id.course_id)

            formatted_course = serializer.data
            formatted_course.update(
                {'period': course_discipline_object.period})
            return formatted_course
        except:
            return None

    def show_discipline(self, instance):
        try:
            serializer = CourseDisciplineSerializer(instance.discipline_id)
            discipline = serializer.data

            return discipline
        except:
            return None
        
    def show_class(self, instance):
        try:
            serializer = ClassSerializer(instance.class_id)
            teach_class = serializer.data

            return teach_class
        except:
            return None


class DisciplineWithTeachSerializer(serializers.ModelSerializer):
    course = serializers.SerializerMethodField('show_course_period')
    taught_by = serializers.SerializerMethodField('show_taught_by')

    class Meta:
        model = Discipline
        fields = ['id', 'name', 'code', 'workload_in_clock',
                  'workload_in_class', 'is_optional', 'course', 'taught_by']

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
            teach = Teach.objects.filter(
                discipline_id=instance['id'], class_id=instance['class_id'])
            teachers = Teacher.objects.filter(
                id__in=teach.values_list('teacher_id', flat=True))

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
        fields = ['id', 'class_canceled_id', 'teacher_id', 'teacher', 'discipline_id', 'discipline']

    def show_discipline(self, instance):
        
        try:
            discipline = Discipline.objects.get(id=instance.discipline_id.id)

            serializer = DisciplineSerializer(discipline)

            return serializer.data
        except:
            try:
                discipline = Discipline.objects.get(id=instance['discipline_id'].id)

                serializer = DisciplineSerializer(discipline)

                return serializer.data
            except:
                return None
    
    def show_teacher(self, instance):
        try:
            discipline = Teacher.objects.get(id=instance['teacher_id'].id)

            serializer = TeacherSerializer(discipline)

            return serializer.data
        except:
            return None

class ClassCanceledScheduleSerializer(serializers.ModelSerializer):
    schedule_class = serializers.SerializerMethodField('show_class', required=False)
    discipline = serializers.SerializerMethodField('show_discipline', required=False)
    requested_by = serializers.SerializerMethodField('show_requested_by', required=False)
    
    class Meta:
        model = Schedule
        fields = ['id', 'quantity', 'weekday', 'start_time','end_time', 'class_id','discipline_id', 'discipline', 'schedule_class', 'requested_by']

    def show_class(self, instance):
        serializer = ClassSerializer(instance.class_id)

        return serializer.data

    def show_discipline(self, instance):
        discipline = Discipline.objects.get(id=instance.discipline_id.id)

        serializer = DisciplineSerializer(discipline)

        return serializer.data
    
    def show_requested_by(self, instance):
        teacher = Teacher.objects.get(id=self.context['teacher_id'])

        serializer = TeacherSerializer(teacher)

        return serializer.data

class ClassCanceledSerializer(serializers.ModelSerializer):
    schedule = serializers.SerializerMethodField('show_schedule')
    schedule_class = serializers.SerializerMethodField('show_schedule_class')

    class Meta:
        model = ClassCanceled
        fields = ['id', 'schedule_id', 'schedule', 'canceled_date', 'reason', 'canceled_by', 'teacher_to_replace', 'replace_class_status', 'schedule_class']

    def show_schedule(self, instance):
        try:
            schedule = Schedule.objects.get(id=instance['schedule_id'].id)
        
            serializer = ClassCanceledScheduleSerializer(schedule, context={ 'teacher_id': instance.canceled_by })
            
            return serializer.data
        except:
            try:
                schedule = Schedule.objects.get(id=instance.schedule_id.id)
        
                serializer = ClassCanceledScheduleSerializer(schedule, context={ 'teacher_id': instance.canceled_by })
                
                return serializer.data
            except:
                return None
            
    def show_schedule_class(self, instance):
        try:
            schedule = Schedule.objects.get(id=instance['schedule_id'].id)

            schedule_class = Class.objects.get(id=schedule.class_id.id)
            serializer = ClassSerializer(schedule_class)

            return serializer.data
        except:
            try:
                schedule = Schedule.objects.get(id=instance.schedule_id.id)

                schedule_class = Class.objects.get(id=schedule.class_id.id)
                serializer = ClassSerializer(schedule_class)

                return serializer.data

            except:
                return None


class ScheduleSerializer(serializers.ModelSerializer):
    discipline = serializers.SerializerMethodField(
        'show_discipline', required=False)
    schedule_class = serializers.SerializerMethodField(
        'show_class', required=False)

    canceled_class = serializers.SerializerMethodField('show_canceled_classes')
    class_to_replace = serializers.SerializerMethodField(
        'show_classes_to_replace')
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

    def show_class_date(self, instance):
        try:
            return instance.date
        except:
            return None

    def show_canceled_classes(self, instance):
        canceled_schedules = ClassCanceled.objects.filter(schedule_id=instance.id)

        reference_date = datetime.strptime(self.context['request'].query_params['date'], '%d/%m/%Y').date(
        ) if 'date' in self.context['request'].query_params else date.today()

        if len(canceled_schedules) > 0:
            week_canceled_schedules = []

            for schedule in canceled_schedules.values():
                current_day = instance.date if hasattr(
                    instance, 'date') else reference_date
                weekday = current_day.weekday()
                next_monday = current_day - timedelta(days=weekday+1)
                weekdates = [next_monday + timedelta(days=x) for x in range(7)]

                if schedule['canceled_date'] in weekdates:
                    schedule['schedule_id'] = schedule['schedule_id_id']
                    week_canceled_schedules.append(schedule)

            serializer = ClassCanceledSerializer(
                data=week_canceled_schedules, many=True)
            serializer.is_valid()

            if len(serializer.data) > 0:
                format_schedule = {'id': week_canceled_schedules[0]['id']}
                format_schedule.update(serializer.data[0])

                return format_schedule

        return None

    def show_classes_to_replace(self, instance):
        
        reference_date = datetime.strptime(self.context['request'].query_params['date'], '%d/%m/%Y').date() if 'date' in self.context['request'].query_params else date.today()

        canceled_schedules = ClassCanceled.objects.filter(schedule_id=instance.id)
        
        if len(canceled_schedules) < 1:
            return None

        classes_to_replace = TemporaryClass.objects.filter(class_canceled_id__id__in=canceled_schedules)
        
        week_replaced_classes = []

        for schedule in classes_to_replace.values():
            current_day = instance.date if hasattr(
                instance, 'date') else reference_date
            weekday = current_day.weekday()
            sunday = current_day - timedelta(days=weekday+1)
            weekdates = [sunday + timedelta(days=x) for x in range(7)]

            canceled_class = ClassCanceled.objects.get(
                id=schedule['class_canceled_id_id'])

            if canceled_class.canceled_date in weekdates:
                if 'student_id' in self.context:
                    if self.context['student_id']:
                        from student.api.serializers import StudentSerializer
                        from student.models import Student

                        try:
                            student = Student.objects.get(id=self.context['student_id'])
                            student_values = StudentSerializer(student)
                            student_disciplines = Discipline.objects.filter(code__in=student_values.data['disciplines']).values_list('code', flat=True)

                            wasReplaced = TemporaryClass.objects.get(class_canceled_id=canceled_class.id)
                            
                            if wasReplaced.discipline_id.code not in student_disciplines:
                                return None 
                        except:
                            pass

                schedule['class_canceled_id'] = schedule['class_canceled_id_id']
                schedule['teacher_id'] = schedule['teacher_id_id']
                schedule['discipline_id'] = schedule['discipline_id_id']

                week_replaced_classes.append(schedule)

        serializer = TemporaryClassSerializer(
            data=week_replaced_classes, many=True)
        serializer.is_valid()

        if len(serializer.data) == 0:
            return None

        return serializer.data[0]

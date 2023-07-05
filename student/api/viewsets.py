from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action

from ..models import Student, StudentAlert
from .serializers import StudentSerializer, StudentAlertSerializer

from teacher.models import Teacher
from course.models import Discipline, Schedule, Class, Course, CourseDiscipline
from course.api.serializers import ScheduleSerializer,DisciplineSerializer, DisciplineWithTeachSerializer

from datetime import date, datetime, timedelta
from utils.generate_month_days import get_days_from_month
import copy

class StudentViewSet(ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer

    def create(self, request):
        student_disciplines = request.data['disciplines']
        student_course = request.data['course']
        student_class_shift = request.data['shift']

        disciplines = Discipline.objects.filter(code__in=student_disciplines)
        course = Course.objects.get(name=student_course)
        
        relation = CourseDiscipline.objects.filter(discipline_id__in=disciplines, course_id=course.id)
        
        period = None
        for course_discipline in relation.values():
            currentPeriod = course_discipline['period']

            if (period == None):
                period = currentPeriod
            elif (currentPeriod is not None and currentPeriod < period):
                period = currentPeriod

        student_class = Class.objects.get(course_id=course, reference_period=period, shift=student_class_shift)
        
        request.data['class_id'] = student_class.id
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        # new_student = Student.objects.create()

        return None
    
    @action(methods=['GET'], detail=False, url_path='byregistration/(?P<student_registration>[^/.]+)')
    def get_student_by_registration(self, request, student_registration):
        try:
            student = Student.objects.get(registration=student_registration)

            serializer = StudentSerializer(student)
            
            return Response(serializer.data, status=status.HTTP_200_OK)
        except:
            return Response(
                {'data': None, 'details': 'Não encontrado'}, status=status.HTTP_200_OK)

    @action(methods=['GET'], detail=False, url_path='(?P<student_id>[^/.]+)/schedules/week')
    def get_week_schedules(self, request, student_id):
        student = Student.objects.get(id=student_id)
        
        disciplines = Discipline.objects.filter(id__in=student.disciplines.values_list('id', flat=True))
        classes = Class.objects.filter(course_id=student.class_id.course_id, shift=student.class_id.shift)
        schedules = Schedule.objects.filter(class_id__in=classes.values_list('id', flat=True), discipline_id__in=disciplines.values_list("id", flat=True))
        
        week_schedules = []
        today_date = datetime.strptime(request.query_params['date'], '%d/%m/%Y').date() if 'date' in request.query_params else date.today()

        for day in range(5):
            today = today_date.weekday()  # Obtém o número do dia da semana atual
            days_diff = day - today  # Calcula a diferença de dias
            
            result = today_date + timedelta(days=days_diff)  # Calcula a data convertida
            print(result)
            for current_schedule in list(schedules):
                if result.weekday() == current_schedule.weekday:
                    copy_of_schedule = copy.copy(current_schedule)
                    copy_of_schedule.date = result
                    week_schedules.append(copy_of_schedule)

        serializer = ScheduleSerializer(week_schedules, many=True, context={'request': request})
        
        return Response(
            serializer.data, status=status.HTTP_200_OK
        )
        
    @action(methods=['GET'], detail=False, url_path='(?P<student_id>[^/.]+)/schedules/month')
    def get_month_schedules(self, request, student_id):
        student = Student.objects.get(id=student_id)

        disciplines = Discipline.objects.filter(id__in=student.disciplines.values_list('id', flat=True))
        classes = Class.objects.filter(course_id=student.class_id.course_id, shift=student.class_id.shift)
        schedules = Schedule.objects.filter(class_id__in=classes.values_list('id', flat=True), discipline_id__in=disciplines.values_list("id", flat=True))
            
        current_month = date.today().month if not self.request.GET.get('month') else self.request.GET.get('month')            
        days_of_month = get_days_from_month(int(current_month))
        
        month_schedules = []
        queryset = list(schedules)

        month_schedules = []

        for week_schedule in days_of_month:

            for current_schedule in queryset:
                if week_schedule.weekday() == current_schedule.weekday:
                    copy_of_schedule = copy.copy(current_schedule)
                    copy_of_schedule.date = week_schedule
                    month_schedules.append(copy_of_schedule)
                
        serializer = ScheduleSerializer(month_schedules, many=True, context={'request': request})

        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(methods=['GET'], detail=False, url_path='(?P<student_id>[^/.]+)/disciplines')
    def get_disciplines(self, request, student_id):
        try:
            student = Student.objects.get(id=student_id)
            disciplines = Discipline.objects.filter(id__in=student.disciplines.values_list('id', flat=True))
            data = []
            for i in disciplines.values():
                i['class_id'] = student.class_id
                data.append(i)
            serializer = DisciplineWithTeachSerializer(data, many=True, context={'request': request})
            
            return Response(
                serializer.data, status=status.HTTP_200_OK
            )
        except:
            return Response(
                {'details': 'Não encontrado'}, status=status.HTTP_404_NOT_FOUND
            )

class StudentAlertViewSet(ModelViewSet):
    queryset = StudentAlert.objects.all()
    serializer_class = StudentAlertSerializer

    def create(self, request, *args, **kwargs):
        discipline = Discipline.objects.get(id=request.data['discipline_id'])
        teacher = Teacher.objects.get(id=request.data['teacher_id'])
        student = Student.objects.get(id=request.data['student_id'])
        reason = request.data['reason'] if 'reason' in request.data else None
        
        alert_create = StudentAlert.objects.create(discipline_id=discipline,
                                                   student_id=student,
                                                   teacher_id=teacher,
                                                   reason = reason)
        alert_create.save()

        alert = StudentAlert.objects.last()
        
        serializer = StudentAlertSerializer(alert)

        return Response(serializer.data, status=status.HTTP_201_CREATED)
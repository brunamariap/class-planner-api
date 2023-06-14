from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework import serializers
from rest_framework.decorators import action

from ..models import Student, StudentAlert
from .serializers import StudentSerializer, StudentAlertSerializer

from course.models import Discipline, Schedule, Class, TemporaryClass, ClassCanceled
from course.api.serializers import ScheduleSerializer,DisciplineSerializer

from datetime import datetime, timedelta, date
from utils.generate_month_days import get_days_from_month
import copy


class StudentViewSet(ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    
    @action(methods=['GET'], detail=False, url_path='(?P<student_id>[^/.]+)/schedules/week')
    def get_week_schedules(self, request, student_id):
        try:
            student = Student.objects.get(id=student_id)
            
            disciplines = Discipline.objects.filter(id__in=student.disciplines.values_list('id', flat=True))
            classes = Class.objects.filter(course_id=student.class_id.course_id)
            schedules = Schedule.objects.filter(class_id__in=classes.values_list('id', flat=True), discipline_id__in=disciplines.values_list("id", flat=True))
            
            serializer = ScheduleSerializer(schedules, many=True, context={'request': request})
            
            return Response(
                serializer.data, status=status.HTTP_200_OK
            )
        except:
            return Response(
                {'details': 'Não encontrado'}, status=status.HTTP_400_BAD_REQUEST
            )
        
    @action(methods=['GET'], detail=False, url_path='(?P<student_id>[^/.]+)/schedules/month')
    def get_month_schedules(self, request, student_id):
        student = Student.objects.get(id=student_id)

        disciplines = Discipline.objects.filter(id__in=student.disciplines.values_list('id', flat=True))
        classes = Class.objects.filter(course_id=student.class_id.course_id)
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
            
            serializer = DisciplineSerializer(disciplines, many=True, context={'request': request})
            
            return Response(
                serializer.data, status=status.HTTP_200_OK
            )
        except:
            return Response(
                {'details': 'Não encontrado'}, status=status.HTTP_400_BAD_REQUEST
            )

class StudentAlertViewSet(ModelViewSet):
    queryset = StudentAlert.objects.all()
    serializer_class = StudentAlertSerializer

    def create(self, request, *args, **kwargs):
        discipline = Discipline.objects.get(id=request.data['discipline_id'])
        student = Student.objects.get(id=request.data['student_id'])
        reason = request.data['reason'] if 'reason' in request.data else None
        
        alert_create = StudentAlert.objects.create(discipline_id=discipline,
                                                   student_id=student,
                                                   reason = reason)
        alert_create.save()

        serializer = StudentAlertSerializer(StudentAlert.objects.last())

        return Response(serializer.data, status=status.HTTP_201_CREATED)
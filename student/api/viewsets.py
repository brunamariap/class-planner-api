from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework import serializers
from rest_framework.decorators import action

from ..models import Student, StudentAlert
from .serializers import StudentSerializer, StudentAlertSerializer

from course.models import Discipline, Schedule, Class, TemporaryClass, ClassCanceled
from course.api.serializers import ScheduleSerializer

from datetime import datetime, timedelta, date

class StudentViewSet(ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    
    @action(methods=['GET'], detail=False, url_path='(?P<student_id>[^/.]+)/schedules/week')
    def get_week_schedules(self, request, student_id):
        student = Student.objects.get(id=student_id)
        
        disciplines = Discipline.objects.filter(id__in=student.disciplines.values_list('id', flat=True))
        classes = Class.objects.filter(course_id=student.class_id.course_id)
        schedules = Schedule.objects.filter(class_id__in=classes.values_list('id', flat=True), discipline_id__in=disciplines.values_list("id", flat=True))
        
        serializer = ScheduleSerializer(schedules, many=True, context={'request': request})
        
        return Response(
            serializer.data, status=status.HTTP_200_OK
        )

class StudentAlertViewSet(ModelViewSet):
    queryset = StudentAlert.objects.all()
    serializer_class = StudentAlertSerializer
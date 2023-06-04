from rest_framework.viewsets import ModelViewSet
from ..models import Student, StudentAlert
from course.models import Discipline, Schedule, Class, TemporaryClass, ClassCanceled
from course.api.serializers import ScheduleSerializer
from .serializers import StudentSerializer, StudentAlertSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework import serializers
from rest_framework.decorators import action
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
        
        queryset = list(schedules)
        print(queryset)
        classes_to_replace = TemporaryClass.objects.filter(discipline_id__in=disciplines.values_list("id", flat=True))
        
        if (classes_to_replace):
            
            for schedule in classes_to_replace.values():
                canceled = ClassCanceled.objects.get(id=schedule['class_canceled_id_id'])
                
                current_day = date.today() if not hasattr(self.request.GET.get('date'), 'date') else datetime.strptime(self.request.GET.get('date'), '%d/%m/%Y').date()
                
                weekday = current_day.weekday()
                sunday = current_day - timedelta(days=weekday+1)
                weekdates = [sunday + timedelta(days=x) for x in range(7)]
                
                replace = Schedule.objects.get(id=canceled.schedule_id.id)
                
                replace.quantity = schedule['quantity']
                replace.temporary_class_id = schedule
                replace.discipline_id = Discipline.objects.get(id=schedule['discipline_id_id'])
                
                if canceled.canceled_date in weekdates:
                    queryset.append(replace)
        
        serializer = ScheduleSerializer(schedules, many=True, context={'request': request})
        
        return Response(
            serializer.data, status=status.HTTP_200_OK
        )


class StudentAlertViewSet(ModelViewSet):
    queryset = StudentAlert.objects.all()
    serializer_class = StudentAlertSerializer
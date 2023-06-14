from rest_framework.viewsets import ModelViewSet
from rest_framework import generics
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from ..models import Teacher

from course.models import Discipline, Class, Teach, Schedule, CourseDiscipline, ClassCanceled, TemporaryClass
from course.api.serializers import DisciplineWithTeachSerializer, ClassSerializer, ScheduleSerializer

from .serializers import TeacherSerializer
from course.api.serializers import TeachSerializer

import calendar
from datetime import date, timedelta, datetime
from utils.generate_month_days import get_days_from_month
import copy


class TeacherViewSet(ModelViewSet):
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer

    @action(methods=['post'], detail=False, url_path='disciplines')
    def create_teacher_binding(self, request):
        class_id = request.data['class_id']
        teacher_id = request.data['teacher_id']
        discipline_id = request.data['discipline_id']

        already_exists = Teach.objects.filter(
            class_id=class_id, teacher_id=teacher_id, discipline_id=discipline_id)
        if (already_exists):
            return Response({"message": "Professor já está vinculado a esta turma"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = TeachSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        headers = self.get_success_headers(serializer.data)

        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    @action(methods=['GET'], detail=False, url_path='(?P<teacher_id>[^/.]+)/schedules/week')
    def get_teacher_week_schedules(self, request, teacher_id):
        teach = Teach.objects.filter(teacher_id=teacher_id)

        disciplines = Discipline.objects.filter(id__in=teach.values_list('discipline_id', flat=True)).values_list('id', flat=True)
        classes = Class.objects.filter(id__in=teach.values_list('class_id', flat=True)).values_list('id', flat=True)
        schedules = Schedule.objects.filter(class_id__in=classes, discipline_id__in=disciplines)

        serializer = ScheduleSerializer(schedules, many=True, context={'request': request})

        return  Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(methods=['GET'], detail=False, url_path='(?P<teacher_id>[^/.]+)/schedules/month')
    def get_teacher_month_schedules(self, request, teacher_id):
        teach = Teach.objects.filter(teacher_id=teacher_id)

        disciplines = Discipline.objects.filter(id__in=teach.values_list('discipline_id', flat=True)).values_list('id', flat=True)
        classes = Class.objects.filter(id__in=teach.values_list('class_id', flat=True)).values_list('id', flat=True)
        schedules = Schedule.objects.filter(class_id__in=classes, discipline_id__in=disciplines)

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

class TeacherDisciplinesViewSet(generics.ListAPIView):

    queryset = Discipline.objects.all()
    serializer_class = DisciplineWithTeachSerializer

    def get_queryset(self):
        try:
            teacher_id = self.kwargs['teacher']
            teach = Teach.objects.filter(
                teacher_id=teacher_id).values_list('discipline_id', flat=True)
            queryset = []
            for id in teach:
                queryset.append(Discipline.objects.get(id=id))

            return queryset
        except ValueError:
            print(ValueError)
            pass

class TeacherClassesViewSet(generics.ListAPIView):

    queryset = Class.objects.all()
    serializer_class = ClassSerializer

    def get_queryset(self):
        try:
            teacher_id = self.kwargs['teacher']
            teach = Teach.objects.filter(
                teacher_id=teacher_id).values_list('class_id', flat=True).distinct()

            queryset = []
            for id in teach:
                queryset.append(Class.objects.get(id=id))

            return queryset
        except:
            pass

class TeacherBindingViewSet(generics.DestroyAPIView):
    queryset = Teach.objects.all()
    serializer_class = TeachSerializer
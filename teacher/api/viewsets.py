from rest_framework.viewsets import ModelViewSet
from rest_framework import generics
from ..models import Teacher

from course.models import Discipline, Class, Teach, Schedule, CourseDiscipline, ClassCanceled, TemporaryClass
from course.api.serializers import DisciplineWithTeachSerializer, ClassSerializer, ScheduleSerializer

from .serializers import TeacherSerializer
from course.api.serializers import TeachSerializer

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from datetime import date, timedelta, datetime

class TeacherViewSet(ModelViewSet):
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer

    @action(methods=['post'], detail=False, url_path='disciplines')
    def create_teacher_binding(self, request):
        class_id = request.data['class_id']
        teacher_id = request.data['teacher_id']

        already_exists = Teach.objects.filter(
            class_id=class_id, teacher_id=teacher_id)
        if (already_exists):
            return Response({"message": "Professor já está vinculado a esta turma"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = TeachSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        headers = self.get_success_headers(serializer.data)

        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

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

class TeacherSchedulesViewSet(generics.ListAPIView):
    queryset = Schedule.objects.all()
    serializer_class = ScheduleSerializer

    def get_queryset(self):
        teacher_id = self.kwargs['teacher']
        teach = Teach.objects.filter(teacher_id=teacher_id)

        disciplines = Discipline.objects.filter(id__in=teach.values_list('discipline_id', flat=True)).values_list('id', flat=True)
        classes = Class.objects.filter(id__in=teach.values_list('class_id', flat=True)).values_list('id', flat=True)
        schedules = Schedule.objects.filter(class_id__in=classes, discipline_id__in=disciplines)

        queryset = list(schedules)

        canceled_schedule = ClassCanceled.objects.filter(schedule_id__id__in=schedules.values_list('id', flat=True))
        classes_to_replace = TemporaryClass.objects.filter(class_canceled_id__id__in=canceled_schedule)

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
                

            return queryset

        return queryset
    
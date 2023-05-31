from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from ..models import Course, Class, Discipline, CourseDiscipline, Schedule, TemporaryClass, ClassCanceled
from .serializers import CourseSerializer, ClassSerializer, DisciplineSerializer, ScheduleSerializer, TemporaryClassSerializer, ClassCanceledSerializer, CourseDisciplinePeriodSerializer
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime,date
from rest_framework import generics

class CourseViewSet(ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer


class DisciplineViewSet(ModelViewSet):
    queryset = Discipline.objects.all()
    serializer_class = DisciplineSerializer

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            courses_length = request.data['course_period']

            serializer.save()
            for i in range(len(courses_length)):
                course_create = CourseDiscipline.objects.create(discipline_id=Discipline.objects.all().last(),
                                                                course_id=Course.objects.get(
                                                                    id=request.data['course_period'][i]['course_id']),
                                                                period=request.data['course_period'][i]['period'])
                course_create.save()

            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        except:
            pass
    

class CourseDisciplinesGenericView(generics.ListAPIView):
    queryset = CourseDiscipline.objects.all()
    serializer_class = CourseDisciplinePeriodSerializer

    def get_queryset(self):
        try:
            course_id = self.kwargs['course']
            disciplines = CourseDiscipline.objects.filter(course_id=course_id)

            disciplines_ids = []
            for obj in disciplines:
                disciplines_ids.append(obj.discipline_id.id)

            disciplines = CourseDiscipline.objects.filter(discipline_id__in=disciplines_ids)
            serializer = self.get_serializer(disciplines, many=True)
            return serializer.data
        except:
            pass


class ClassViewSet(ModelViewSet):
    queryset = Class.objects.all()
    serializer_class = ClassSerializer


    # def getWeekSchedules():
    #     schedules = Schedule.objects.all()

    # @action(methods=['get'], detail=False, url_path='<teacher_id:teacher>/schedules/week')
    # def getTeacherSchedules(self, request):
        
    #     schedules = Schedule.objects.get()
    #     serializer = ScheduleSerializer()

    #     return Response(serializer.data, status=status.HTTP_200_OK)


class ScheduleViewSet(ModelViewSet):
    queryset = Schedule.objects.all()
    serializer_class = ScheduleSerializer

    @action(methods=['post'], detail=False, url_path='cancel')
    def cancelSchedule(self, request):
        try:
            schedule_id = request.data['schedule_id']
            canceled_date = datetime.strptime(request.data['canceled_date'], "%d/%m/%Y")

            schedule = Schedule.objects.get(id=schedule_id)
            if not (schedule.weekday == canceled_date.weekday()):
                return Response({'message': 'Esta aula normalmente não ocorre na data informada'}, status=status.HTTP_400_BAD_REQUEST)

            already_exists = ClassCanceled.objects.filter(
                    schedule_id=schedule_id, canceled_date=canceled_date)
            if (already_exists):
                return Response({'message': 'Esta aula já foi cancelada na data informada'}, status=status.HTTP_400_BAD_REQUEST)

            serializer = ClassCanceledSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            headers = self.get_success_headers(serializer.data)

            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        except:
            return Response({"message": "Ocorreu um erro ao tentar esta funcionalidade"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    @action(methods=['delete'], detail=False, url_path='cancel/(?P<class_canceled_id>[^/.]+)')
    def cancelClassCancellation(self, request, class_canceled_id):
        try:
            class_canceled = ClassCanceled.objects.get(id=class_canceled_id)
            class_canceled.delete()

            return Response(status=status.HTTP_204_NO_CONTENT)
        except:
            return Response({"message": "Ocorreu um erro ao tentar esta funcionalidade"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class TemporaryClassViewSet(ModelViewSet):
    queryset = TemporaryClass.objects.all()
    serializer_class = TemporaryClassSerializer

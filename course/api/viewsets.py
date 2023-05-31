from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from ..models import Course, Class, Discipline, CourseDiscipline, Schedule
from .serializers import CourseSerializer, ClassSerializer, DisciplineSerializer, CourseDisciplinePeriodSerializer, ScheduleSerializer


class CourseViewSet(ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    """ @action(methods=['GET'], detail=False, url_path='(?P<pk>[^/.]+)/disciplines')
    def get_course_disciplines(self, request, *args, **kwargs):
        
            course_id = self.kwargs['pk']
            print(course_id)
            course_disciplines = Discipline.objects.filter(course_id=course_id)
            print(course_disciplines)
            disciplines = Discipline.objects.filter(id__in=course_disciplines)
            serializer = DisciplineSerializer(disciplines, many=True)

            return Response(serializer.data, status=status.HTTP_200_OK) """

class DisciplineViewSet(ModelViewSet):
    queryset = Discipline.objects.all()
    serializer_class = DisciplineSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        courses_length = request.data['course_period']
        
        serializer.save()
        for i in range(len(courses_length)):
            course_create = CourseDiscipline.objects.create(discipline_id=Discipline.objects.all().last(),
                                                            course_id=Course.objects.get(id=request.data['course_period'][i]['course_id']),
                                                            period=request.data['course_period'][i]['period']) 
            course_create.save()

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    

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

    """ def create(self, request, *args, **kwargs):

        course_data = Course.objects.get(id=request.data.get("course_id"))
        
        try:
            serializer = self.get_serializer(data=request.data) 
            serializer.is_valid(raise_exception=True)

            serializer.validated_data['course_id'] = course_data
            serializer.save()

            headers = self.get_success_headers(serializer.data)

            return Response(
                serializer.data, status=status.HTTP_201_CREATED, headers=headers
            )

        except:
            pass

    # def getWeekSchedules():
    #     schedules = Schedule.objects.all()

    # @action(methods=['get'], detail=False, url_path='<teacher_id:teacher>/schedules/week')
    # def getTeacherSchedules(self, request):
        
    #     schedules = Schedule.objects.get()
    #     serializer = ScheduleSerializer()

    #     return Response(serializer.data, status=status.HTTP_200_OK)"""

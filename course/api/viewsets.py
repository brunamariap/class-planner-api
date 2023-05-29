from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from ..models import Course, Class, Discipline, CourseDiscipline, Schedule
from .serializers import CourseSerializer, ClassSerializer, DisciplineSerializer, ScheduleSerializer
from rest_framework.response import Response
from rest_framework import status


class CourseViewSet(ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

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

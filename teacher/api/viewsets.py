from rest_framework.viewsets import ModelViewSet
from ..models import Teacher

from course.models import Discipline, Class, Teach
from course.api.serializers import DisciplineSerializer, ClassSerializer

from .serializers import TeacherSerializer
from course.api.serializers import TeachSerializer

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

class TeacherViewSet(ModelViewSet):
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer

    @action(methods=['get'], detail=False, url_path='<id:teacher>/disciplines')
    def getTeacherDisciplines(self, request):
        id = request.data.get('id')
        teach = Teach.objects.get(teacher_id=id)
        disciplines = Discipline.objects.get(teach=teach)

        serializer = DisciplineSerializer(disciplines, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(methods=['post'], detail=False, url_path='disciplines')
    def createTeacherBinding(self, request):
        serializer = TeachSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
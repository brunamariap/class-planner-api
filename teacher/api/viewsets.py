from rest_framework.viewsets import ModelViewSet
from ..models import Teacher
from .serializers import TeacherSerializer
from course.api.serializers import TeachSerializer

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

class TeacherViewSet(ModelViewSet):
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer

    # @action(methods=['get'], detail=False, url_path='disciplines')
    # def getTeacherDisciplines(self, request):
    #     pass

    @action(methods=['post'], detail=False, url_path='disciplines')
    def createTeacherBinding(self, request):
        serializer = TeachSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
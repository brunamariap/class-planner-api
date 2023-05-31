from rest_framework.viewsets import ModelViewSet
from rest_framework import generics
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
    
    @action(methods=['post'], detail=False, url_path='disciplines')
    def create_teacher_binding(self, request):
        serializer = TeachSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
class TeacherDisciplinesViewSet(generics.ListAPIView):

    queryset = Discipline.objects.all()
    serializer_class = DisciplineSerializer

    def get_queryset(self):
        try:
            teacher_id = self.kwargs['teacher']
            teach = Teach.objects.get(teacher_id=teacher_id)

            return self.queryset.filter(teach=teach)
        except:
            pass

class TeacherClassesViewSet(generics.ListAPIView):

    queryset = Class.objects.all()
    serializer_class = ClassSerializer

    def get_queryset(self):
        try:
            teacher_id = self.kwargs['teacher']
            teach = Teach.objects.get(teacher_id=teacher_id)

            return self.queryset.filter(teach=teach)
        except:
            pass
from rest_framework.viewsets import ModelViewSet
from ..models import Teacher
from .serializers import TeacherSerializer

from rest_framework.decorators import action
from rest_framework.response import Response

class TeacherViewSet(ModelViewSet):
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer
from rest_framework.viewsets import ModelViewSet
from ..models import Student, StudentAlert
from .serializers import StudentSerializer, StudentAlertSerializer
from rest_framework.response import Response
from rest_framework import status


class StudentViewSet(ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer

class StudentAlertViewSet(ModelViewSet):
    queryset = StudentAlert.objects.all()
    serializer_class = StudentAlertSerializer
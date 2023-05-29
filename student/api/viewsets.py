from rest_framework.viewsets import ModelViewSet
from ..models import Student, StudentAlert
from course.models import Discipline
from .serializers import StudentSerializer, StudentAlertSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework import serializers

class StudentViewSet(ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    
    # def create(self, request):
    #     disciplines = request.data.get('disciplines')

    #     for discipline_code in disciplines:
    #         discipline_id = Discipline.objects.filter(code=discipline_code)

    #         if (discipline_id):
    #             print(discipline_id)
    #     print(request.data.get('disciplines'))

    #     # serializer = self.get_serializer(data=request.data) 
    #     # serializer.is_valid(raise_exception=True)

    #     # serializer.validated_data['course_id'] = course_data
    #     # serializer.save()
        
    #     # headers = self.get_success_headers(serializer.data)

    #     return Response(
    #         {"message": "Socrro"}, status=status.HTTP_201_CREATED
    #     )


class StudentAlertViewSet(ModelViewSet):
    queryset = StudentAlert.objects.all()
    serializer_class = StudentAlertSerializer
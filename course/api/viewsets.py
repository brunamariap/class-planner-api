from rest_framework.viewsets import ModelViewSet
from ..models import Course, Class, Discipline
from .serializers import CourseSerializer, ClassSerializer, DisciplineSerializer
from rest_framework.response import Response
from rest_framework import status


class CourseViewSet(ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

class DisciplineViewSet(ModelViewSet):
    queryset = Discipline.objects.all()
    serializer_class = DisciplineSerializer

class ClassViewSet(ModelViewSet):
    queryset = Class.objects.all()
    serializer_class = ClassSerializer

    def create(self, request, *args, **kwargs):

        course_data = Course.objects.get(id=request.data.get("course_id"))
        
        shift = request.data.get("shift")
        reference_period = request.data.get("reference_period")

        class_shift = Class.objects.filter(shift=shift, reference_period=reference_period)
        
        if (len(class_shift) > 0):
            return Response(
                {
                    "message": "Já existe uma turma com esse período e turno"
                }, status=status.HTTP_400_BAD_REQUEST
            )
    
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
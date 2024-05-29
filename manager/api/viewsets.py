from rest_framework.viewsets import ModelViewSet
from ..models import Course, Class
from .serializers import CourseSerializer, ClassSerializer
from rest_framework.response import Response
from rest_framework import status


class CourseViewSet(ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

class ClassViewSet(ModelViewSet):
    queryset = Class.objects.all()
    serializer_class = ClassSerializer

    def create(self, request, *args, **kwargs):
        class_data = Course.objects.get(id=request.data.get("class_id"))

        try:
            serializer = self.get_serializer(data=request.data) 
            serializer.is_valid(raise_exception=True)

            serializer.validated_data['class_id'] = class_data
            serializer.save()
            headers = self.get_success_headers(serializer.data)
            return Response(
                serializer.data, status=status.HTTP_201_CREATED, headers=headers
            )

        except:
            pass
from rest_framework.viewsets import ModelViewSet
from rest_framework import generics
from ..models import Teacher

from course.models import Discipline, Class, Teach
from course.api.serializers import DisciplineWithTeachSerializer, ClassSerializer

from .serializers import TeacherSerializer
from course.api.serializers import TeachSerializer

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response


class TeacherViewSet(ModelViewSet):
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer

    @action(methods=['post'], detail=False, url_path='disciplines')
    def createTeacherBinding(self, request):
        class_id = request.data['class_id']
        teacher_id = request.data['teacher_id']

        already_exists = Teach.objects.filter(
            class_id=class_id, teacher_id=teacher_id)
        if (already_exists):
            return Response({"message": "Professor já está vinculado a esta turma"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = TeachSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        headers = self.get_success_headers(serializer.data)

        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    # @action(methods=['delete'], detail=False, url_path='teach/<int:teach>')
    # def removeTeacherBinding(self, request, pk=None, discipline_id=None):
    #     binding_id = request.data.get('id')
    #     binding = Teach.objects.get(id=binding_id)

    #     binding.delete()

    #     return Response({'message': 'Vínculo excluído com sucesso'}, status=status.HTTP_204_NO_CONTENT)


class TeacherDisciplinesViewSet(generics.ListAPIView):

    queryset = Discipline.objects.all()
    serializer_class = DisciplineWithTeachSerializer

    def get_queryset(self):
        try:
            teacher_id = self.kwargs['teacher']
            teach = Teach.objects.filter(
                teacher_id=teacher_id).values_list('discipline_id', flat=True)
            queryset = []
            for id in teach:
                queryset.append(Discipline.objects.get(id=id))

            return queryset
        except ValueError:
            print(ValueError)
            pass


class TeacherClassesViewSet(generics.ListAPIView):

    queryset = Class.objects.all()
    serializer_class = ClassSerializer

    def get_queryset(self):
        try:
            teacher_id = self.kwargs['teacher']
            teach = Teach.objects.filter(
                teacher_id=teacher_id).values_list('class_id', flat=True).distinct()
            
            queryset = []
            for id in teach:
                queryset.append(Class.objects.get(id=id))

            return queryset
        except:
            pass

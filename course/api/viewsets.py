from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from ..models import Course, Class, Discipline, CourseDiscipline, Schedule, TemporaryClass, ClassCanceled
from .serializers import CourseSerializer, ClassSerializer, DisciplineSerializer, ScheduleSerializer, TemporaryClassSerializer, ClassCanceledSerializer
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime,date
from django.db.models import Sum

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
                                                            course_id=Course.objects.get(
                                                                id=request.data['course_period'][i]['course_id']),
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


class ScheduleViewSet(ModelViewSet):
    queryset = Schedule.objects.all()
    serializer_class = ScheduleSerializer

    
    @action(methods=['GET','POST'], detail=False, url_path='canceled')
    def cancelSchedule(self, request):
        
        if (request.method == 'GET'):
            canceled_classes = ClassCanceled.objects.all()
            serializer = ClassCanceledSerializer(many=True, data=canceled_classes)
            serializer.is_valid()

            return Response(serializer.data, status=status.HTTP_200_OK)
        elif (request.method == 'POST'):
            schedule_id = request.data['schedule_id']
            canceled_date = datetime.strptime(request.data['canceled_date'], "%d/%m/%Y")

            schedule = Schedule.objects.get(id=schedule_id)
            if not (schedule.weekday == canceled_date.weekday()):
                return Response({'message': 'Esta aula normalmente não ocorre na data informada'}, status=status.HTTP_400_BAD_REQUEST)

            already_exists = ClassCanceled.objects.filter(
                    schedule_id=schedule_id, canceled_date=canceled_date)
            if (already_exists):
                return Response({'message': 'Esta aula já foi cancelada na data informada'}, status=status.HTTP_400_BAD_REQUEST)
            
            if (schedule.quantity < request.data['quantity_available']):
                return Response({'message': f'Quantidade solicitada para disponibilizar aulas é maior que a quantidade ofertada no horário selecionado. Há {schedule.quantity} aulas desta disciplina'}, status=status.HTTP_400_BAD_REQUEST)

            serializer = ClassCanceledSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            headers = self.get_success_headers(serializer.data)

            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        
    @action(methods=['DELETE'], detail=False, url_path='canceled/(?P<class_canceled_id>[^/.]+)')
    def cancelClassCancellation(self, request, class_canceled_id):
        try:
            class_canceled = ClassCanceled.objects.get(id=class_canceled_id)
            class_canceled.delete()

            return Response(status=status.HTTP_204_NO_CONTENT)
        except:
            return Response({"message": "Ocorreu um erro ao tentar esta funcionalidade"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class TemporaryClassViewSet(ModelViewSet):
    queryset = TemporaryClass.objects.all()
    serializer_class = TemporaryClassSerializer

    def create(self, request):
        already_replaced = TemporaryClass.objects.filter(class_canceled_id=request.data['class_canceled_id']).aggregate(total_quantity=Sum('quantity'))
        
        if (already_replaced['total_quantity']):
            class_canceled = ClassCanceled.objects.get(id=request.data['class_canceled_id'])
            remaining_amount = class_canceled.quantity_available - already_replaced['total_quantity']

            if (remaining_amount > 0 and request.data['quantity'] > remaining_amount):
                return Response({"message": f"Quantidade solicitada é superior a disponível. Há {remaining_amount} aulas disponíveis"}, status=status.HTTP_400_BAD_REQUEST)
            elif (remaining_amount < 1):
                return Response({"message": "Não há mais aulas disponíveis para serem substituídas"}, status=status.HTTP_400_BAD_REQUEST)
            
            class_canceled.quantity_available = remaining_amount - request.data['quantity']
            class_canceled.save()
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        class_canceled = ClassCanceled.objects.get(id=instance.class_canceled_id.id)
        class_canceled.quantity_available += instance.quantity
        class_canceled.save()

        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

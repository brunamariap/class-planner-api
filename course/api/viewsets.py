from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status, generics

from ..models import Course, Class, Discipline, CourseDiscipline, Schedule, TemporaryClass, ClassCanceled, Teach
from .serializers import CourseSerializer, ClassSerializer, CourseClassesSerializer, DisciplineSerializer, ScheduleSerializer, TemporaryClassSerializer, ClassCanceledSerializer, CourseDisciplinePeriodSerializer, DisciplineWithTeachSerializer

from student.models import Student
from student.api.serializers import ClassStudentsSerializer

from utils.generate_month_days import get_days_from_month
from utils.report_canceled_class import report_canceled_class

from datetime import date, datetime
from django.db.models import Sum
import math
import copy


class CourseViewSet(ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    @action(methods=['GET'], detail=False, url_path='(?P<course_id>[^/.]+)/classes')
    def get_classes_of_courses(self, request, course_id, *args, **kwargs):
        try:
            classes = Class.objects.filter(course_id=course_id)
            serializer = CourseClassesSerializer(classes, many=True)

            return Response(serializer.data, status=status.HTTP_200_OK)
        except:
            return Response({"message": "Ocorreu um erro ao tentar esta funcionalidade"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    @action(methods=['GET'], detail=False, url_path='(?P<course_id>[^/.]+)/disciplines')
    def get_disciplines_of_courses(self, request, course_id, *args, **kwargs):
        try:
            disciplines = CourseDiscipline.objects.filter(course_id=course_id)
            serializer = CourseDisciplinePeriodSerializer(disciplines, many=True)

            return Response(serializer.data, status=status.HTTP_200_OK)
        except:
            return Response({"message": "Ocorreu um erro ao tentar esta funcionalidade"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    @action(methods=['DELETE'], detail=False, url_path='(?P<course_id>[^/.]+)/disciplines/(?P<discipline_id>[^/.]+)')
    def destroy_discipline_link(self, request, course_id, discipline_id, *args, **kwargs):
        try:
            discipline_link_exists = CourseDiscipline.objects.filter(discipline_id=discipline_id)

            if discipline_link_exists:
                course_discipline = CourseDiscipline.objects.filter(course_id=course_id, discipline_id=discipline_id)
                if course_discipline:
                    course_discipline.delete()

                    if discipline_link_exists.count() == 1:
                        discipline = Discipline.objects.get(id=discipline_id)
                        discipline.delete()
                
            return Response([], status=status.HTTP_204_NO_CONTENT)
        except:
            return Response({"message": "Ocorreu um erro ao tentar esta funcionalidade"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DisciplineViewSet(ModelViewSet):
    queryset = Discipline.objects.all()
    serializer_class = DisciplineSerializer

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            associations_with_discipline = request.data['course']

            for i in range(len(associations_with_discipline)):
                course_link_already_exists = CourseDiscipline.objects.filter(discipline_id=Discipline.objects.last(),
                                                                             course_id=Course.objects.get(
                                                                                id=request.data['course'][i]['course_id']))

                if not course_link_already_exists:
                    create_course_link = CourseDiscipline.objects.create(discipline_id=Discipline.objects.last(),
                                                                         course_id=Course.objects.get(
                                                                            id=request.data['course'][i]['course_id']),
                                                                         period=request.data['course'][i]['period'])
                    create_course_link.save()
                
                """ if course_link_already_exists:
                    return Response({"message": "A associação dessa disciplina com esse curso já existe"}, status=status.HTTP_400_BAD_REQUEST) """

            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        except:
            return Response({"message": "Ocorreu um erro ao tentar esta funcionalidade"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def update(self, request, *args, **kwargs):
        try:
            partial = kwargs.pop('partial', False)
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)

            associations_with_discipline = request.data['course']
            courses_associated_with_discipline = CourseDiscipline.objects.filter(discipline_id=Discipline.objects.get(id=self.kwargs['pk'])).values_list('course_id', flat=True)

            for i in range(len(associations_with_discipline)):
                course_link_already_exists = True if request.data['course'][i]['course_id'] in courses_associated_with_discipline else None

                if not course_link_already_exists:
                    create_course_link = CourseDiscipline.objects.create(discipline_id=Discipline.objects.get(id=self.kwargs['pk']),
                                                                         course_id=Course.objects.get(
                                                                            id=request.data['course'][i]['course_id']),
                                                                         period=request.data['course'][i]['period'])
                    create_course_link.save()

            if getattr(instance, '_prefetched_objects_cache', None):
                # If 'prefetch_related' has been applied to a queryset, we need to
                # forcibly invalidate the prefetch cache on the instance.
                instance._prefetched_objects_cache = {}

            return Response(serializer.data, status=status.HTTP_200_OK)
        except:
            return Response({"message": "Ocorreu um erro ao tentar esta funcionalidade"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ImportDisciplineGenericView(generics.CreateAPIView):  
    queryset = Discipline.objects.all()
    serializer_class = DisciplineSerializer

    def create(self, request, *args, **kwargs):
        try:
            disciplines_json_list = request.data
            all_disciplines = Discipline.objects.all().values()
            list_codes = [object['code'] for object in all_disciplines]
            course_obj = Course.objects.get(id=self.kwargs['course'])

            for discipline in disciplines_json_list:
                period = None if discipline['Período'] == '-' else int(discipline['Período'])

                if not discipline['Sigla'] in list_codes:
                    list_codes.append(discipline['Sigla'])
                    is_optional = discipline['Optativo']
                    workload_in_class = int(discipline['CH Componente'][-2:])
    
                    discipline_dict = {
                        "name":discipline['Componente'],
                        "code":discipline['Sigla'],
                        "is_optional": True if is_optional == 'Sim' else False,
                        "workload_in_class":workload_in_class,
                        "workload_in_clock":int(math.ceil(workload_in_class*45)/60),
                        "course":[
                            {
                                "course_id": course_obj,
                                "period": period
                            }
                        ]
                    }

                    serializer = self.get_serializer(data=discipline_dict)
                    serializer.is_valid(raise_exception=True)
                    serializer.save()

                    course_link_already_exists = CourseDiscipline.objects.filter(discipline_id=Discipline.objects.last(),
                                                                                 course_id=course_obj,
                                                                                 period=period)
                
                    if course_link_already_exists:
                        return Response({"message": "A associação dessa disciplina com esse curso já existe"}, status=status.HTTP_400_BAD_REQUEST)

                    course_create = CourseDiscipline.objects.create(discipline_id=Discipline.objects.all().last(),
                                                                    course_id=course_obj,
                                                                    period=period)
                    course_create.save()
                else:
                    discipline_code = discipline['Sigla']
                    discipline_obj = Discipline.objects.get(code=discipline_code)
                    
                    course_link_already_exists = CourseDiscipline.objects.filter(discipline_id=discipline_obj,
                                                                                 course_id=course_obj,
                                                                                 period=period)
                
                    if course_link_already_exists:
                        return Response({"message": "A associação dessa disciplina com esse curso já existe"}, status=status.HTTP_400_BAD_REQUEST)
                    
                    course_create = CourseDiscipline.objects.create(discipline_id=discipline_obj,
                                                                    course_id=course_obj,
                                                                    period=period)
                    course_create.save()

            return Response(status=status.HTTP_204_NO_CONTENT)
        except:
           return Response({"message": "Ocorreu um erro ao tentar esta funcionalidade"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ClassViewSet(ModelViewSet):
    queryset = Class.objects.all()
    serializer_class = ClassSerializer

    def create(self, request, *args, **kwargs):
        class_already_exists = Class.objects.filter(course_id=request.data['course_id'],
                                                    reference_period=request.data['reference_period'],
                                                    shift=request.data['shift'])
        
        if class_already_exists:
            return Response({"message": "A turma já existe"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
    
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    
    @action(methods=['GET'], detail=False, url_path='(?P<class_id>[^/.]+)/disciplines')
    def get_class_disciplines(self, request, class_id):
        
        student_class = Class.objects.get(id=class_id)
        
        course_discipline = CourseDiscipline.objects.filter(period=student_class.reference_period, course_id=student_class.course_id.id)
        disciplines = Discipline.objects.filter(id__in=course_discipline.values_list('discipline_id',flat=True))
        
        queryset = []
        for i in disciplines.values():
            i['class_id'] = class_id
            queryset.append(i)
        
        serializer = DisciplineWithTeachSerializer(data=queryset, many=True)
        serializer.is_valid()
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    @action(methods=['GET'], detail=False, url_path='(?P<class_id>[^/.]+)/students')
    def get_class_students(self, request, class_id):
        try:
            students = Student.objects.filter(class_id=class_id)
            serializer = ClassStudentsSerializer(students, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)
    
    @action(methods=['GET'], detail=False, url_path='(?P<class_id>[^/.]+)/schedules/week')
    def get_week_schedules(self, request, class_id):
        
        schedules = Schedule.objects.filter(class_id=class_id)
        serializer = ScheduleSerializer(schedules, many=True, context={'request': request})

        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(methods=['GET'], detail=False, url_path='(?P<class_id>[^/.]+)/schedules/month')
    def get_month_schedules(self, request, class_id):
        schedules = Schedule.objects.filter(class_id=class_id)
            
        current_month = date.today().month if not self.request.GET.get('month') else self.request.GET.get('month')            
        days_of_month = get_days_from_month(int(current_month))
        
        month_schedules = []
        queryset = list(schedules)

        month_schedules = []

        for week_schedule in days_of_month:

            for current_schedule in queryset:
                if week_schedule.weekday() == current_schedule.weekday:
                    copy_of_schedule = copy.copy(current_schedule)
                    copy_of_schedule.date = week_schedule
                    month_schedules.append(copy_of_schedule)
                
        serializer = ScheduleSerializer(month_schedules, many=True, context={'request': request})
        
        return Response(serializer.data, status=status.HTTP_200_OK)

class ScheduleViewSet(ModelViewSet):
    queryset = Schedule.objects.all()
    serializer_class = ScheduleSerializer

    def get_queryset(self):
        queryset = Schedule.objects.all()
        
        return queryset

    # def destroy(self, request, class_id):
    #     try:
    #         print(class_id)
    #         instance = Schedule.objects.get(id=class_id)
    #         instance.delete()
        
    #         return Response(status=status.HTTP_204_NO_CONTENT)
    #     except:
    #         return Response({"detail": "Não encontrado"},status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['GET','POST'], detail=False, url_path='canceled')
    def cancel_schedule(self, request):
        
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
            class_canceled = ClassCanceled.objects.last()

            report_canceled_class(class_canceled)

            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        
    @action(methods=['DELETE'], detail=False, url_path='canceled/(?P<class_canceled_id>[^/.]+)')
    def cancel_class_cancellation(self, request, class_canceled_id):
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

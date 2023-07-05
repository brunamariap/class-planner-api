from rest_framework import serializers
from course.api.serializers import DisciplineSerializer, TeacherSerializer, ClassSerializer
from course.models import Discipline, CourseDiscipline, Teach, Teacher, Class
from ..models import Student, StudentAlert


class StudentSerializer(serializers.ModelSerializer):
    disciplines = serializers.SlugRelatedField(queryset=Discipline.objects.all(), slug_field='code', required=False, many=True)
    student_class = serializers.SerializerMethodField('show_class')
    class Meta:
        model = Student
        fields = ['id','class_id', 'name', 'registration', 'avatar', 'email','student_class', 'disciplines']

    def show_class(self, instance):
        try:
            student_class = Class.objects.get(id=instance.class_id.id)
            serializer = ClassSerializer(student_class)
            
            return serializer.data
        except:
            return None

class ClassStudentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ['id', 'name', 'registration', 'avatar', 'disciplines']


class StudentAlertSerializer(serializers.ModelSerializer):
    student = serializers.SerializerMethodField('show_student')
    discipline = serializers.SerializerMethodField('show_discipline')
    teacher = serializers.SerializerMethodField('show_teacher')

    class Meta:
        model = StudentAlert
        fields = ['id', 'teacher_id', 'student_id', 'discipline_id','created_at', 'reason',  'teacher', 'student', 'discipline']

    def show_student(self, instance):
        try:
            student = Student.objects.get(id=instance.student_id.id)
            serializer = StudentSerializer(student)
            
            return serializer.data
        except:
            return None
    
    def show_discipline(self, instance):
        try:
            discipline = Discipline.objects.get(id=instance.discipline_id.id)
            serializer = DisciplineSerializer(discipline)
            
            return serializer.data
        except:
            return None
    
    def show_teacher(self, instance):
        try:
            teacher = Teacher.objects.get(id=instance.teacher_id.id)
            serializer = TeacherSerializer(teacher)
            
            return serializer.data
        except:
            return None
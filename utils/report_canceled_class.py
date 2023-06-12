from django.core.mail import send_mail
from student.models import Student
from course.models import Class, Course
from config.settings import EMAIL_HOST_USER


def report_canceled_class(canceled_class):
    course_id = canceled_class.schedule_id.class_id.course_id
    discipline = canceled_class.schedule_id.discipline_id
    classes_ids = Class.objects.filter(course_id=course_id)

    students = Student.objects.filter(class_id__in=classes_ids, disciplines=discipline)

    discipline_name = discipline.name.split('-')[1]
    schedule = canceled_class.schedule_id

    send_mail(
        'Aula cancelada', 
        f'A aula de{discipline_name} que aconteceria no dia {canceled_class.canceled_date} das {schedule.start_time} às {schedule.end_time} foi cancelada', 
        EMAIL_HOST_USER, 
        [student.email for student in students]
    )
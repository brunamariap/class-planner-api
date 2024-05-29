from django.core.mail import send_mail
from student.models import Student
from course.models import Class
from config.settings import EMAIL_HOST_USER
from datetime import date, time


def report_canceled_class(canceled_class):
    course_id = canceled_class.schedule_id.class_id.course_id
    discipline = canceled_class.schedule_id.discipline_id
    classes_ids = Class.objects.filter(course_id=course_id)
    students = Student.objects.filter(class_id__in=classes_ids, disciplines=discipline)

    discipline_name = discipline.name.split('-')[1]
    discipline_name = discipline_name.lstrip()
    discipline_name = discipline_name[:discipline_name.index('(') if '(' in discipline_name else None]
    
    schedule = canceled_class.schedule_id
    canceled_date = date.strftime(canceled_class.canceled_date, "%d/%m/%Y")
    start_time = time.strftime(schedule.start_time, "%H:%M")
    end_time = time.strftime(schedule.end_time, "%H:%M")
    
    message = f'A aula de {discipline_name} que aconteceria no dia {canceled_date} das {start_time} às {end_time} foi cancelada'

    send_mail(
        'Aula cancelada', 
        message, 
        EMAIL_HOST_USER, 
        [student.email for student in students]
    )
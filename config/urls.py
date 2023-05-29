from django.contrib import admin
from django.urls import path

from django.conf.urls import include
from rest_framework import routers
from course.api.viewsets import CourseViewSet, ClassViewSet, DisciplineViewSet
from teacher.api.viewsets import TeacherViewSet, TeacherClassesViewSet, TeacherDisciplinesViewSet
from student.api.viewsets import StudentViewSet, StudentAlertViewSet
from course.api.viewsets import CourseViewSet

router = routers.SimpleRouter()

router.register('courses', CourseViewSet)
router.register('classes', ClassViewSet)
router.register('disciplines', DisciplineViewSet)
router.register('teachers', TeacherViewSet)
router.register('students', StudentViewSet)
router.register('alerts', StudentAlertViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('teachers/<int:teacher>/disciplines/', TeacherDisciplinesViewSet.as_view()),
    path('teachers/<int:teacher>/classes/', TeacherClassesViewSet.as_view()),
]

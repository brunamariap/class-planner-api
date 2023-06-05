from django.contrib import admin
from django.urls import path

from django.conf.urls import include
from rest_framework import routers
from course.api.viewsets import CourseViewSet, ClassViewSet, DisciplineViewSet, CourseDisciplinesGenericView, ScheduleViewSet, TemporaryClassViewSet, ImportDisciplineGenericView
from teacher.api.viewsets import TeacherViewSet, TeacherClassesViewSet, TeacherDisciplinesViewSet, TeacherBindingViewSet, TeacherSchedulesViewSet
from student.api.viewsets import StudentViewSet, StudentAlertViewSet
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

router = routers.SimpleRouter()

router.register('courses', CourseViewSet)
router.register('classes', ClassViewSet)
router.register('disciplines', DisciplineViewSet)
router.register('teachers', TeacherViewSet)
router.register('students', StudentViewSet)
router.register('alerts', StudentAlertViewSet)
router.register('schedules', ScheduleViewSet)
router.register('temporary-classes', TemporaryClassViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/teachers/disciplines/<int:pk>/', TeacherBindingViewSet.as_view()),
    path('api/courses/<int:course>/disciplines/import/', ImportDisciplineGenericView.as_view()),
    path('api/courses/<int:course>/disciplines/', CourseDisciplinesGenericView.as_view()),
    path('api/teachers/<int:teacher>/disciplines/', TeacherDisciplinesViewSet.as_view()),
    path('api/teachers/<int:teacher>/classes/', TeacherClassesViewSet.as_view()),
    path('api/teachers/<int:teacher>/schedules/', TeacherSchedulesViewSet.as_view()),

    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger'),
    path('api/docs/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

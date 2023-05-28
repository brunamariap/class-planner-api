from django.urls import path, include
from rest_framework import routers
from .api.viewsets import CourseViewSet, ClassViewSet


router = routers.DefaultRouter()
router.register('courses', CourseViewSet)
router.register('classes', ClassViewSet)


urlpatterns = [
    path("api/", include(router.urls)),
]
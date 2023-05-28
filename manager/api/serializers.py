from rest_framework import serializers
from ..models import Manager


class ManagerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Manager
        fields = ['id', 'name', 'degree', 'course_load', 'byname']
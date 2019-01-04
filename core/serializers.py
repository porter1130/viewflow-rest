from rest_framework import serializers
from viewflow.models import Task


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'


class NodeSerializer(serializers.Serializer):
    name = serializers.CharField()
    title = serializers.CharField()

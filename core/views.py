from django.shortcuts import render

# Create your views here.
from rest_framework import mixins
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from viewflow.models import Task

from core import serializers


class TaskViewSet(GenericViewSet, mixins.ListModelMixin):
    serializer_class = serializers.TaskSerializer

    def get_queryset(self):
        queryset = Task.objects.all()
        return queryset

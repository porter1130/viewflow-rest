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
        status_list = self.request.query_params.getlist('status', None)
        queryset = Task.objects.filter(owner=self.request.user, flow_task_type='HUMAN')
        if status_list is not None:
            queryset = queryset.filter(status__in=status_list)
        return queryset

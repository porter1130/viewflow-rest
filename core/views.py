from django.shortcuts import render

# Create your views here.
from rest_framework import mixins
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from viewflow import STATUS
from viewflow.models import Task

from core import serializers
from demo.business import Node


class TaskViewSet(GenericViewSet, mixins.ListModelMixin):
    serializer_class = serializers.TaskSerializer

    def get_queryset(self):
        status_list = self.request.query_params.getlist('status', None)
        task_type = self.request.query_params.get('task_type', 'HUMAN')
        queryset = Task.objects.filter(owner=self.request.user, flow_task_type=task_type)
        if status_list is not None:
            queryset = queryset.filter(status__in=status_list)
        return queryset


class WithdrawNodesView(GenericAPIView, mixins.ListModelMixin):
    serializer_class = serializers.NodeSerializer

    def get_queryset(self):
        process_id = self.request.query_params.get('processId', None)
        task_id = self.request.query_params.get('taskId', None)

        withdrawable_nodes = []
        tasks = Task.objects.filter(process__id=process_id, flow_task_type='HUMAN').order_by('id')
        current_task = tasks.get(pk=task_id)

        for task in tasks:
            if task.status == STATUS.DONE and task.flow_task.name != current_task.flow_task.name:
                if not any(filter(lambda x: x.name == task.flow_task.name, withdrawable_nodes)):
                    withdrawable_nodes.append(
                        Node(name=task.flow_task.name, title=task.flow_task.task_title))

        return withdrawable_nodes

    def get(self, request, *args, **kwargs):
        return self.list(request, args, kwargs)

import sys

from django.contrib.auth.models import User
from django.shortcuts import render

# Create your views here.
from rest_framework import mixins
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from viewflow.managers import ProcessQuerySet, TaskQuerySet
from viewflow.models import Process, Task


class StartView(GenericAPIView):

    def post(self, request, *args, **kwargs):
        exc = True
        try:
            try:
                flow_task = self.kwargs.get('flow_task', None)
                # process = Process.objects.filter(id=1).first()
                activation = flow_task.activation_class()
                activation.initialize(flow_task, None)

                activation.prepare(request.POST or None, user=self.request.user)
                activation.done()
                return Response(data=None)
            except Exception:
                exc = False
                if activation.lock:
                    activation.lock.__exit__(*sys.exc_info())
                raise
        finally:
            if exc and activation.lock:
                activation.lock.__exit__(None, None, None)


class ApprovalView(GenericAPIView):

    def post(self, request, *args, **kwargs):
        task = TaskQuerySet(model=Task).get(pk=self.kwargs.get('task_pk', None))
        flow_task = task.flow_task
        flow_class = flow_task.flow_class
        lock = task.flow_task.flow_class.lock_impl(flow_class.instance)
        with lock(flow_class, task.process.id):
            # task = get_object_or_404(flow_task.flow_class.task_class._default_manager, pk=task_pk,
            #                          process_id=process_pk)
            activation = flow_task.activation_class()
            activation.initialize(flow_task, task)

            activation.prepare(request.POST or None)
            activation.done()

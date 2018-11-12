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
                flow_class = self.kwargs.get('flow_class', None)
                # process = Process.objects.filter(id=1).first()
                activation = flow_class.start.activation_class()
                activation.initialize(flow_class.start, None)

                user = User.objects.first()
                activation.prepare(request.POST or None, user=user)
                activation.done()
                return Response(data=flow_class.process_title)
            except:
                exc = False
                if activation.lock:
                    activation.lock.__exit__(*sys.exc_info())
                raise
        finally:
            if exc and activation.lock:
                activation.lock.__exit__(None, None, None)


class ApproveView(GenericAPIView):

    def post(self, request, flow_class, flow_task, **kwargs):
        return Response(data=flow_class.process_title)

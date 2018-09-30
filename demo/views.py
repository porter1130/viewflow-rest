from django.contrib.auth.models import  User
from django.shortcuts import render

# Create your views here.
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from viewflow.managers import ProcessQuerySet
from viewflow.models import Process

from demo.models import HelloWorldProcess


class StartView(GenericAPIView):

    def post(self, request, *args, **kwargs):
        flow_class = self.kwargs.get('flow_class', None)
        # process = Process.objects.filter(id=1).first()
        activation = flow_class.start.activation_class()
        activation.initialize(flow_class.start, None)

        user=User.objects.first()
        activation.prepare(request.POST or None, user=user)
        activation.done()
        return Response(data=flow_class.process_title)


class ApproveView(GenericAPIView):

    def post(self, request, flow_class, flow_task, **kwargs):
        return Response(data=flow_class.process_title)

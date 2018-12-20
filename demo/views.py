import sys

from django.contrib.auth.models import User
from django.shortcuts import render

# Create your views here.
from rest_framework import mixins
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from viewflow.managers import ProcessQuerySet, TaskQuerySet
from viewflow.models import Process, Task

from core.mixins import StartWorkflowMixin, WorkflowMixin


class StartView(StartWorkflowMixin):

    def post(self, request, *args, **kwargs):
        return Response(data='success')


class ApprovalView(WorkflowMixin):

    def post(self, request, *args, **kwargs):
        return Response(data=None)

import sys


# Create your views here.
from rest_framework.response import Response

from core.mixins import StartWorkflowMixin, WorkflowMixin


class StartView(StartWorkflowMixin):

    def post(self, request, *args, **kwargs):
        return Response(data='success')


class DraftView(WorkflowMixin):

    def post(self, request, *args, **kwargs):
        return Response(data='success')


class ApprovalView(WorkflowMixin):

    def post(self, request, *args, **kwargs):
        return Response(data=None)

from rest_framework.response import Response

from core.mixins import  WorkflowActionMixin


class RedirectTaskView(WorkflowActionMixin):
    """Redirect the task."""

    def post(self, request, *args, **kwargs):
        return Response(data='success')

    def perform(self):
        self.activation.redirect()

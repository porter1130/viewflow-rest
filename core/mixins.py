from django.utils.decorators import method_decorator
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import GenericAPIView
from viewflow.decorators import flow_start_view, flow_view

from core.decorators import workflow_start_view, workflow_view


class StartWorkflowMixin(GenericAPIView):
    fields = None

    def activation_done(self):
        self.activation.done()

    @method_decorator(flow_start_view)
    def dispatch(self, request, **kwargs):
        """Check user permissions, and prepare flow for execution."""
        self.activation = request.activation
        # if not self.activation.has_perm(request.user):
        #     raise PermissionDenied
        super(StartWorkflowMixin, self).dispatch(request, **kwargs)
        self.activation.prepare(request.POST or None, user=request.user)
        self.activation_done()
        return self.response


class WorkflowMixin(GenericAPIView):
    fields = None

    def activation_done(self):
        self.activation.done()

    @method_decorator(flow_view)
    def dispatch(self, request, **kwargs):
        self.activation = request.activation

        super(WorkflowMixin, self).dispatch(request, **kwargs)

        self.activation.prepare(request.POST or None, user=request.user)
        self.activation_done()
        return self.response

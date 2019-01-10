from django.conf.urls import url
from django.urls import reverse
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


class WorkflowActionMixin(GenericAPIView):

    def perform(self):
        self.activation.perform()

    @method_decorator(flow_view)
    def dispatch(self, request, **kwargs):
        self.activation = request.activation

        super(WorkflowActionMixin, self).dispatch(request, **kwargs)
        self.activation.prepare(request.POST or None, user=request.user)
        self.perform()
        return self.response


class RedirectViewMixin(object):
    redirect_view_class = None

    def __init__(self, *args, **kwargs):  # noqa D102
        self._redirect_view = kwargs.pop('redirect_view', None)
        super(RedirectViewMixin, self).__init__(*args, **kwargs)

    @property
    def redirect_view(self):
        """View for the admin to redirect a task."""
        return self._redirect_view if self._redirect_view else self.redirect_view_class.as_view()

    def urls(self):
        """Add `/<process_pk>/<task_pk>/redirect/` url."""
        urls = super(RedirectViewMixin, self).urls()
        urls.append(
            url(r'^(?P<process_pk>\d+)/{}/(?P<task_pk>\d+)/redirect/$'.format(self.name),
                self.redirect_view, {'flow_task': self}, name="{}__redirect".format(self.name))
        )
        return urls

    def get_task_url(self, task, url_type='guess', namespace='', **kwargs):
        """Handle for url_type='redirect'."""
        if url_type in ['redirect']:
            url_name = '{}:{}__redirect'.format(namespace, self.name)
            return reverse(url_name, args=[task.process_id, task.pk])
        return super(RedirectViewMixin, self).get_task_url(task, url_type, namespace=namespace, **kwargs)

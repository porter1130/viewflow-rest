from viewflow.flow.views.actions import BaseTaskActionView
from viewflow.flow.views.mixins import FlowTaskManagePermissionMixin


class RedirectTaskView(FlowTaskManagePermissionMixin, BaseTaskActionView):
    """Redirect the task."""

    action_name = 'redirect'
    action_title = _('跳转')

    def can_proceed(self):
        """Check that node can be undone."""
        return self.activation.redirect.can_proceed()

    def perform(self):
        """Redirect the node."""
        self.activation.redirect()

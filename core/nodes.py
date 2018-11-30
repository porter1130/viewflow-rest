from copy import copy

from viewflow import mixins, Gateway
from viewflow.flow import views
from viewflow.nodes.view import BaseView

from core.activations import ApprovalActivation


class Approval(mixins.PermissionMixin, BaseView):
    task_type = 'SPLIT'
    activation_class = ApprovalActivation

    activate_next_view_class = views.ActivateNextTaskView
    cancel_view_class = views.CancelTaskView
    detail_view_class = views.DetailTaskView
    undo_view_class = views.UndoTaskView
    assign_view_class = views.AssignTaskView
    unassign_view_class = views.UnassignTaskView

    def __init__(self, wait_all=True, **kwargs):
        super(Approval, self).__init__(**kwargs)
        self._wait_all = wait_all
        self.owner_list = None

    def Assign(self, owner_list=None, **owner_kwargs):
        """
        Assign task to the User immediately on activation.

        Accepts user lookup kwargs or callable :: Process -> User::

            .Assign(username='employee')
            .Assign(lambda process: process.created_by)
        """
        result = copy(self)

        if owner_list:
            result.owner_list = owner_list
        else:
            result.owner_list = owner_kwargs
        return result

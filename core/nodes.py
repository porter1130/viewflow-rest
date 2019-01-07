from copy import copy

from django.conf.urls import url
from django.urls import reverse
from viewflow import mixins, Gateway, STATUS
from viewflow.flow import views
from viewflow.nodes.view import BaseView
from viewflow.utils import is_owner

from core.actions import RedirectTaskView
from core.activations import ApprovalActivation
from core.mixins import RedirectViewMixin


class Approval(mixins.PermissionMixin, RedirectViewMixin, BaseView):
    task_type = 'HUMAN'
    activation_class = ApprovalActivation

    activate_next_view_class = views.ActivateNextTaskView
    cancel_view_class = views.CancelTaskView
    detail_view_class = views.DetailTaskView
    undo_view_class = views.UndoTaskView
    assign_view_class = views.AssignTaskView
    unassign_view_class = views.UnassignTaskView
    redirect_view_class = RedirectTaskView

    def __init__(self, wait_all=True, **kwargs):

        self._assign_view = kwargs.pop('assign_view', None)
        self._unassign_view = kwargs.pop('unassign_view', None)
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

    @property
    def assign_view(self):
        """View to assign task to the user."""
        return self._assign_view if self._assign_view else self.assign_view_class.as_view()

    @property
    def unassign_view(self):
        """View to unassign task from the user."""
        return self._unassign_view if self._unassign_view else self.unassign_view_class.as_view()

    def urls(self):
        """Add /assign/ and /unassign/ task urls."""
        urls = super(Approval, self).urls()
        urls.append(url(r'^(?P<process_pk>\d+)/{}/(?P<task_pk>\d+)/assign/$'.format(self.name),
                        self.assign_view, {'flow_task': self}, name="{}__assign".format(self.name)))
        urls.append(url(r'^(?P<process_pk>\d+)/{}/(?P<task_pk>\d+)/unassign/$'.format(self.name),
                        self.unassign_view, {'flow_task': self}, name="{}__unassign".format(self.name)))
        return urls

    def get_task_url(self, task, url_type='guess', namespace='', **kwargs):
        """Handle `assign`, `unassign` and `execute` url_types.

        If url_type is `guess` task check is it can be assigned, unassigned or executed.
        If true, the action would be returned as guess result url.
        """
        user = kwargs.get('user', None)

        # assign
        if url_type in ['assign', 'guess']:
            if task.status == STATUS.NEW and self.can_assign(user, task):
                url_name = '{}:{}__assign'.format(namespace, self.name)
                return reverse(url_name, kwargs={'process_pk': task.process_id, 'task_pk': task.pk})

        # execute
        if url_type in ['execute', 'guess']:
            if task.status == STATUS.ASSIGNED and self.can_execute(user, task):
                url_name = '{}:{}'.format(namespace, self.name)
                return reverse(url_name, kwargs={'process_pk': task.process_id, 'task_pk': task.pk})

        # unassign
        if url_type in ['unassign']:
            if task.status == STATUS.ASSIGNED and self.can_unassign(user, task):
                url_name = '{}:{}__unassign'.format(namespace, self.name)
                return reverse(url_name, kwargs={'process_pk': task.process_id, 'task_pk': task.pk})

        return super(Approval, self).get_task_url(task, url_type, namespace=namespace, **kwargs)

    def calc_owner(self, activation):
        """Determine a user to auto-assign the task."""
        from django.contrib.auth import get_user_model

        owner = self._owner
        if callable(owner):
            owner = owner(activation)
        elif isinstance(owner, dict):
            owner = get_user_model()._default_manager.get(**owner)
        return owner

    def calc_owner_permission(self, activation):
        """Determine required permission to assign and execute this task."""
        owner_permission = self._owner_permission
        if callable(owner_permission):
            owner_permission = owner_permission(activation)
        return owner_permission

    def can_assign(self, user, task):
        """Check if user can assign the task."""
        # already assigned
        if task.owner_id:
            return False

        # user not logged in
        if user is None or user.is_anonymous:
            return False

        # available for everyone
        if not task.owner_permission:
            return True

        # User have the permission
        obj = None
        if self._owner_permission_obj:
            if callable(self._owner_permission_obj):
                obj = self._owner_permission_obj(task.process)
            else:
                obj = self._owner_permission_obj

        return user.has_perm(task.owner_permission, obj=obj)

    def can_unassign(self, user, task):
        """Check if user can unassign the task."""
        # not assigned
        if task.owner_id is None:
            return False

        # user not logged in
        if user is None or user.is_anonymous:
            return False

        # Assigned to the same user
        if is_owner(task.owner, user):
            return True

        # User have flow management permissions
        return user.has_perm(self.flow_class._meta.manage_permission_name)

    def can_execute(self, user, task):
        """Check user premition to execute the task."""
        if task.owner_permission is None and task.owner is None:
            return True

        return is_owner(task.owner, user)

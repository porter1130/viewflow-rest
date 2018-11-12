from django.utils.timezone import now
from viewflow import signals
from viewflow.activation import Activation, STATUS, all_leading_canceled
from viewflow.exceptions import FlowRuntimeError


class ApprovalActivation(Activation):

    def __init__(self, **kwargs):
        self.next_task = None
        super(ApprovalActivation, self).__init__(**kwargs)

    @Activation.status.transition(source=STATUS.NEW, target=STATUS.STARTED)
    def start(self):
        """Create Join task on the first incoming node complete."""
        self.task.save()
        signals.task_started.send(sender=self.flow_class, process=self.process, task=self.task)

    @Activation.status.transition(source=STATUS.STARTED)
    def done(self):
        """Complete the join within current exception propagation strategy."""
        with self.exception_guard():
            self.task.finished = now()
            self.set_status(STATUS.DONE)
            self.task.save()

            signals.task_finished.send(sender=self.flow_class, process=self.process, task=self.task)

            self.activate_next()

    def is_done(self):
        """Check that process can be continued futher.

        Join check the all task state in db with the common token prefix.

        Join node would continue execution if all incoming tasks are DONE or CANCELED.
        """
        if not self.flow_task._wait_all:
            return True

        join_prefixes = set(
            prev.token.get_common_split_prefix(self.task.token, prev.pk)
            for prev in self.task.previous.exclude(status=STATUS.CANCELED).all())

        if len(join_prefixes) > 1:
            raise FlowRuntimeError('Multiple tokens {} came to join {}'.format(join_prefixes, self.flow_task.name))

        join_token_prefix = next(iter(join_prefixes))

        active = self.flow_class.task_class._default_manager \
            .filter(process=self.process, token__startswith=join_token_prefix) \
            .exclude(status__in=[STATUS.DONE, STATUS.CANCELED])

        return not active.exists()

    @Activation.status.transition(source=STATUS.ERROR)
    def retry(self):
        """Manual join gateway reactivation after an error."""
        if self.is_done():
            self.done.original()

    @Activation.status.transition(
        source=[STATUS.ERROR, STATUS.DONE],
        target=STATUS.STARTED,
        conditions=[all_leading_canceled])
    def undo(self):
        """Undo the task."""
        super(ApprovalActivation, self).undo.original()

    @Activation.status.transition(source=[STATUS.NEW, STATUS.STARTED])
    def perform(self):
        """Manual gateway activation."""
        if self.is_done():
            self.done.original()

    @Activation.status.transition(source=[STATUS.NEW, STATUS.STARTED], target=STATUS.CANCELED)
    def cancel(self):
        """Cancel existing join."""
        super(ApprovalActivation, self).cancel.original()

    def activate_next(self):
        pass

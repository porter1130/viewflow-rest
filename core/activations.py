from django.utils.timezone import now
from viewflow import signals
from viewflow.activation import Activation, STATUS, all_leading_canceled
from viewflow.exceptions import FlowRuntimeError
from viewflow.token import Token


class ApprovalActivation(Activation):

    def __init__(self, **kwargs):
        self.next_task = None
        self.tasks = []
        self._split_count = None
        super(ApprovalActivation, self).__init__(**kwargs)

    def calculate_next(self):
        self._split_count = self.flow_task.task_count_callback(self.process)

    def activate_next(self):
        pass

    @Activation.status.transition(source=STATUS.NEW)
    def assign_tasks(self):
        with self.exception_guard():
            self.task.started = now()
            self.task.save()

            self.calculate_next()

            self.task.finished = now()
            self.set_status(STATUS.DONE)
            self.task.save()

            if self._split_count:
                token_source = Token.split_token_source(self.task.token, self.task.pk)
                for _ in range(self._split_count):
                    task = self.flow_class.task_class(
                        process=self.process,
                        flow_task=self.flow_task,
                        token=next(token_source),
                        previous=self.task.previous
                    )
                    task.save()
            elif self.flow_task._ifnone_next_node is not None:
                self.flow_task._ifnone_next_node.activate(prev_activation=self, token=self.task.token)
            else:
                raise FlowRuntimeError(
                    "{} activated with zero and no IfNone nodes specified".format(self.flow_task.name))

    @classmethod
    def activate(cls, flow_task, prev_activation, token):
        flow_class, flow_task = flow_task.flow_class, flow_task
        process = prev_activation.process

        task = flow_class.task_class(
            process=process,
            flow_task=flow_task,
            token=token
        )

        task.save()
        task.previous.add(prev_activation.task)

        activation = cls()
        activation.initialize(flow_task, task)
        activation.assign_tasks()

        return activation

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

    @Activation.status.transition(source=STATUS.STARTED)
    def done(self):
        """Complete the join within current exception propagation strategy."""
        with self.exception_guard():
            self.task.finished = now()
            self.set_status(STATUS.DONE)
            self.task.save()

            #todo:cancel other tasks

            signals.task_finished.send(sender=self.flow_class, process=self.process, task=self.task)

            self.activate_next()

    @Activation.status.transition(source=[STATUS.NEW, STATUS.STARTED])
    def perform(self):
        """Manual gateway activation."""
        if self.is_done():
            self.done.original()

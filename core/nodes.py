from viewflow import mixins, Gateway

from core.activations import ApprovalActivation


class Approval(mixins.TaskDescriptionMixin,
               mixins.NextNodeMixin,
               Gateway):
    task_type = 'HUMAN'
    activation_class = ApprovalActivation

    def __init__(self, wait_all=True, **kwargs):
        super(Approval, self).__init__(**kwargs)
        self._wait_all = wait_all

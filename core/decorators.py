import sys

from django.db import transaction
import functools


def workflow_start_view(view):
    @transaction.atomic
    @functools.wraps(view)
    def _wrapper(request, flow_task, **kwargs):
        exc = True
        try:
            try:
                activation = flow_task.activation_class()
                activation.initialize(flow_task, None)

                request.activation = activation
                request.process = activation.process
                request.task = activation.task
                return view(request, **kwargs)
            except Exception:
                exc = False
                if activation.lock:
                    activation.lock.__exit__(*sys.exc_info())
                raise
        finally:
            if exc and activation.lock:
                activation.lock.__exit__(None, None, None)

    return _wrapper

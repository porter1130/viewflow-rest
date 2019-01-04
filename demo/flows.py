from django.contrib.auth.models import User
from viewflow import flow, frontend
from viewflow.base import Flow, this
from viewflow.flow.views import CreateProcessView, UpdateProcessView

from core.nodes import Approval
from demo import views
from demo.models import HelloWorldProcess
from demo.views import ApprovalView, StartView


@frontend.register
class HelloWorldFlow(Flow):
    process_class = HelloWorldProcess

    start = (
        flow.Start(
            StartView
        ).Permission(auto_create=True).Next(this.approve)
    )

    # approve = (
    #     flow.View(
    #         UpdateProcessView,
    #         fields=["approved"]
    #     ).Assign(owner=User.objects.filter(username__in=['porter']).first()).Permission(auto_create=True).Next(this.check_approve)
    # )
    approve = (
        Approval(
            view_or_class=ApprovalView,
            wait_all=False,
            task_title='审批'
        ).Assign(owner_list=User.objects.filter(username__in=['porter', 'admin', 'wjc']).all()).Permission(
            auto_create=True).Next(
            this.check_approve)
    )

    check_approve = (
        flow.If(lambda activation: activation.process.approved)
            .Then(this.send)
            .Else(this.approve2)
    )

    send = (
        flow.Handler(
            this.send_hello_world_request
        ).Next(this.end)
    )

    approve2 = (
        Approval(
            view_or_class=ApprovalView,
            task_title='审批2'
        ).Assign(owner_list=User.objects.filter(username__in=['porter', 'admin', 'wjc']).all()).Permission(
            auto_create=True).Next(
            this.end)
    )

    end = flow.End()

    def send_hello_world_request(self, activation):
        print(activation.process.text)

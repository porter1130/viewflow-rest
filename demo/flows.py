from django.contrib.auth.models import User
from viewflow import flow, frontend
from viewflow.base import Flow, this
from viewflow.flow.views import CreateProcessView, UpdateProcessView

from core.nodes import Approval
from demo import views
from demo.models import HelloWorldProcess


@frontend.register
class HelloWorldFlow(Flow):
    process_class = HelloWorldProcess

    start = (
        flow.Start(
            CreateProcessView,
            fields=["text"]
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
            view_or_class=UpdateProcessView,
            fields=["approved"]
        ).Assign(owner_list=User.objects.filter(username__in=['porter', 'admin', 'wjc']).all()).Permission(
            auto_create=True).Next(
            this.check_approve)
    )

    check_approve = (
        flow.If(lambda activation: activation.process.approved)
            .Then(this.send)
            .Else(this.end)
    )

    send = (
        flow.Handler(
            this.send_hello_world_request
        ).Next(this.end)
    )

    end = flow.End()

    def send_hello_world_request(self, activation):
        print(activation.process.text)

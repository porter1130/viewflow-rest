from django.conf.urls import url, include
from viewflow.flow.viewset import FlowViewSet

from demo.flows import HelloWorldFlow

urlpatterns = [
    url(r'^helloworld/', include(FlowViewSet(HelloWorldFlow).urls))
]

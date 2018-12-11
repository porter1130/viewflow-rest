"""viewflow_rest URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from django.views import generic
from material.frontend import urls as frontend_urls
from rest_framework import routers
from rest_framework_jwt.views import obtain_jwt_token

from core.views import TaskViewSet
from demo.flows import HelloWorldFlow
from demo.views import StartView, ApprovalView

router = routers.DefaultRouter(trailing_slash=False)
router.register(r'workflow/tasks', TaskViewSet, base_name='Workflow Tasks')

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^api/workflow/helloworld/start', StartView.as_view(), {'flow_task': HelloWorldFlow.start}),
    url(r'^api/workflow/approval/(?P<task_pk>\d+)$', ApprovalView.as_view()),
    url(r'^api/', include(router.urls)),
    url(r'^api/token$', obtain_jwt_token),
    url(r'^$', generic.RedirectView.as_view(url='/workflow/', permanent=False)),
    url(r'', include(frontend_urls)),

]

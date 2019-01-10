from django.db import models

# Create your models here.
from viewflow.models import Process


class HelloWorldProcess(Process):
    text = models.CharField(max_length=150)
    is_terminate = models.BooleanField(default=False,verbose_name='是否终止')
    approved = models.BooleanField(default=False)

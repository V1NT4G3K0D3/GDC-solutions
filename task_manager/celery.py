import os
from datetime import timedelta

from django.conf import settings

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "task_manager.settings")
app = Celery("task_manager")
app.config_from_object("django.conf:settings")
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

# from celery.decorators import periodic_task

# # Periodic Task
# @periodic_task(run_every=timedelta(seconds=10))
# def every_30_seconds():
#     print("Running Every 30 Seconds!")

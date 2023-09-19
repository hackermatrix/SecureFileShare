# celery.py

from __future__ import absolute_import, unicode_literals
import os
from filesec.celery import Celery
from celery.schedules import crontab

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'filesec.settings')

# Create a Celery instance and configure it using settings from Django's settings.py
app = Celery('filesec')

# Load task modules from all registered Django app configs.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Autodiscover tasks in all installed apps, so you don't need to manually import them.
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))

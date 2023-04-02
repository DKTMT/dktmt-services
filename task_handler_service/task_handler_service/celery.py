import os
from celery import Celery

app = Celery('task_handler_service')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# Use Redis as the message broker
app.conf.broker_url = f'redis://{os.environ["REDIS_HOST"]}:6379/0'

# Use Redis as the result backend
app.conf.result_backend = f'redis://{os.environ["REDIS_HOST"]}:6379/0'

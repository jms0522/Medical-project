# 프로젝트 디렉토리 내 celery.py
from celery import Celery
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chatbot.settings.prod')

app = Celery('chatbot', broker_transport_options={'confirm_publish': True})

app.config_from_object('django.conf:settings', namespace='CELERY')

app.conf.broker_connection_retry_on_startup = True

app.autodiscover_tasks() 
# 프로젝트 디렉토리 내 celery.py
from celery import Celery
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chatbot.settings.base')

app = Celery('chatbot', broker='pyamqp://guest@localhost//')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

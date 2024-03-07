# tasks.py
from celery import shared_task
from chat_app.models import UserInteractionLog
from django.contrib.auth.models import User
from django.utils.dateparse import parse_datetime

@shared_task
def save_log(log_data):
    if 'timestamp' in log_data:
        log_data['timestamp'] = parse_datetime(log_data['timestamp'])

    UserInteractionLog.objects.create(**log_data)

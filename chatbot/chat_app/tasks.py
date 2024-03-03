# tasks.py
from celery import shared_task
from chat_app.models import UserInteractionLog
from django.contrib.auth.models import User

@shared_task
def save_log(log_data):
    user_id = log_data.pop('user_id', None)
    user = User.objects.get(id=user_id) if user_id is not None else None
    
    UserInteractionLog.objects.create(user=user, **log_data)
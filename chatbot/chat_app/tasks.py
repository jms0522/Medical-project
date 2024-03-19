# tasks.py
from celery import shared_task
from .models import ClickEventLog, FormSubmitEventLog, ScrollEventLog, PageViewEventLog, ErrorLog, ChatBot, SimilarAnswer
from django.contrib.auth.models import User
from django.utils.dateparse import parse_datetime
from django.utils import timezone
import json
import logging

logger_error = logging.getLogger('error')

@shared_task
def save_log(log_data):
    if 'timestamp' in log_data:
        log_data['timestamp'] = parse_datetime(log_data['timestamp'])
    event_type = log_data.get('event_type')
        
    common_data = {
        "username": log_data.get('username'),
        "element_class": log_data.get('element_class'),
        "element_name": log_data.get('element_name'),
        "url": log_data.get('url'),
        "timestamp": log_data.get('timestamp'),
    }
        
    # 각 이벤트 유형에 맞는 모델에 데이터 저장
    if event_type == 'click':
        ClickEventLog.objects.create(**common_data)
    elif event_type == 'formSubmit':
        FormSubmitEventLog.objects.create(**common_data)
    elif event_type == 'scroll':
        ScrollEventLog.objects.create(scrollPosition=log_data.get('scrollPosition', None), **common_data)
    elif event_type == 'pageView':
        PageViewEventLog.objects.create(**common_data)
    elif event_type == 'error':
        error_specific_data = {
            "message": log_data.get('message', None),
            "lineno": log_data.get('lineno', None),
        }
        ErrorLog.objects.create(**{**common_data, **error_specific_data})

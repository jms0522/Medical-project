# tasks.py
from celery import shared_task
from .models import ClickEventLog, FormSubmitEventLog, ScrollEventLog, PageViewEventLog, ErrorLog, ChatBot, SimilarAnswer
from django.contrib.auth.models import User
from django.utils.dateparse import parse_datetime
from django.utils import timezone
from django.shortcuts import get_object_or_404
from .services import get_question_handling_chain, get_similar_answers_chain
import json
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
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

@shared_task
def handle_question_task(username, text):
    try:
        question_chain = get_question_handling_chain()
        response_data = question_chain.invoke(text)
        chat_bot_instance = ChatBot.objects.create(username=username, question=text, answer=response_data, created_at=timezone.now())
        
        # 이 부분은 비동기 작업에서 직접 JsonResponse를 반환할 수 없으므로 제거합니다.
        # 대신 작업의 ID와 결과 데이터를 반환합니다.
        return {"id": chat_bot_instance.id, "data": response_data}
    except Exception as e:
        # 비동기 작업에서는 로그를 기록하는 것이 좋습니다.
        logger_error.error(f'Error during question handling: {str(e)}')
        return {"error": str(e)}
    
@shared_task
def fetch_similar_answers_task(question_id, username):
    try:
        original_question = get_object_or_404(ChatBot, id=question_id, username=username)
        similar_answer_instance, created = SimilarAnswer.objects.get_or_create(
            original_question=original_question,
            defaults={'similar_answer': ''}
        )
        
        if created:
            similar_chain = get_similar_answers_chain()
            similar_answer_instance.similar_answer = similar_chain.invoke(original_question.question)
            similar_answer_instance.save()

        # 마찬가지로 JsonResponse 대신 딕셔너리 데이터를 반환합니다.
        return {
            "id": similar_answer_instance.id,
            "originalQuestion": original_question.question,
            "similarAnswer": similar_answer_instance.similar_answer,
            "createdAt": similar_answer_instance.created_at
        }
    except Exception as e:
        logger_error.error(f'Error during fetching similar answers: {str(e)}')
        return {"error": str(e)}
# chatbot
from .services import fetch_similar_answers, handle_question, login_required_ajax
from .models import ChatBot, SimilarAnswer
import json

# django
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.http import HttpResponseRedirect, JsonResponse, HttpResponseNotAllowed
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from .models import ClickEventLog, FormSubmitEventLog, ScrollEventLog, PageViewEventLog, ErrorLog
from .tasks import save_log, handle_question_task, fetch_similar_answers_task
import logging
from django.http import HttpResponse
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

logger_interaction = logging.getLogger('drrc')
logger_error = logging.getLogger('error')

@login_required_ajax
@require_POST  # POST 요청만 허용
def ask_question(request):
    text = request.POST.get("text", "").strip()
    if not text:
        return JsonResponse({"error": "Empty question."}, status=400)
    
    # 비동기 작업으로 질문 처리 Task 호출
    handle_question_task.delay(request.user.username, text)
    
    return JsonResponse({"status": "Processing your question..."}, status=202)

@login_required
def get_similar_answers(request, question_id):
    # 비동기 작업으로 유사 답변 검색 Task 호출
    fetch_similar_answers_task.delay(question_id, request.user.username)
    
    return JsonResponse({"status": "Fetching similar answers..."}, status=202)

def chat(request):
    # 사용자가 로그인한 경우와 로그인하지 않은 경우를 구분하여 처리
    if request.user.is_authenticated:
        username = request.user.username
    else:
        username = None  # 로그인하지 않은 경우, user를 None으로 설정
    chats = ChatBot.objects.filter(username=username)
    return render(request, "chat_bot.html", {"chats": chats})

@login_required
def get_user_chats(request):
    username = request.user.username
    chats = ChatBot.objects.filter(username=username).order_by('created_at')
    chat_data = list(chats.values('username','question', 'answer', 'created_at'))
    return JsonResponse({'chats': chat_data})

@csrf_exempt
def log_interaction(request):
    if request.method == 'POST': # 로그 데이터를 JSON 형식으로 파싱
        data = json.loads(request.body) # 요청에서 사용자 인증 정보를 확인
        event_type = data.get('eventType')

        # 공통 데이터 추출
        common_data = {
            "username": request.user.username if request.user.is_authenticated else None,
            "element_class": data.get('elementClass'),
            "element_name": data.get('elementName'),
            "url": data.get('url', 'unknown'),
            "timestamp": timezone.now(),
        }

        # 이벤트 유형별 데이터 처리 및 저장
        if event_type == 'click':
            ClickEventLog.objects.create(**common_data)
        elif event_type == 'formSubmit':
            FormSubmitEventLog.objects.create(**common_data)
        elif event_type == 'scroll':
            ScrollEventLog.objects.create(scrollPosition=data.get('scrollPosition'), **common_data)
        elif event_type == 'pageView':
            PageViewEventLog.objects.create(**common_data)
        elif event_type == 'error':
            error_specific_data = {
                "message": data.get('message'),
                "lineno": data.get('lineno', None),
            }
            ErrorLog.objects.create(**{**common_data, **error_specific_data})
        else:
            # 처리할 수 없는 이벤트 유형에 대한 처리
            return JsonResponse({"error": "Unsupported event type"}, status=400)

        # 성공적으로 데이터가 처리된 경우
        return JsonResponse({"status": "success"}, status=200)

    # POST 요청이 아닌 경우
    return JsonResponse({"error": "Invalid request"}, status=400)

def metrics(request):
    return HttpResponse(generate_latest(), content_type=CONTENT_TYPE_LATEST)


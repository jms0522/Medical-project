# chatbot
from .services import fetch_similar_answers, handle_question, login_required_ajax
from .models import ChatBot, SimilarAnswer
import json

# django
from django.shortcuts import render
from django.contrib import messages
from django.http import HttpResponseRedirect, JsonResponse, HttpResponseNotAllowed, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import ClickEventLog, FormSubmitEventLog, ScrollEventLog, PageViewEventLog, ErrorLog
from .tasks import save_log
import logging
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from chatbot.metrics import request_latency
import time

logger_interaction = logging.getLogger('drrc')
logger_error = logging.getLogger('error')

# 챗봇 페이지
def chat(request):
    # 사용자가 로그인한 경우와 로그인하지 않은   경우를 구분하여 처리
    if request.user.is_authenticated:
        username = request.user.username
    else:
        username = None  # 로그인하지 않은 경우, user를 None으로 설정
    chats = ChatBot.objects.filter(username=username)
    return render(request, "chat_bot.html", {"chats": chats})

# 챗봇 응답 로직
@login_required_ajax
@csrf_exempt
def ask_question(request):
    logger_error.info(f"Request method: {request.method}")
    start_time = time.time()  # 처리 시작 시간
    if request.method == "POST":
        text = request.POST.get("text", "").strip()
        
        if not text:
            return JsonResponse({"error": "Empty question."}, status=400)
        response = handle_question(request.user.username, text)
        # 요청 처리 시간 측정 및 메트릭 업데이트
        request_latency.labels('ask_question').observe(time.time() - start_time)

        # 비즈니스 로직을 services.py에서 제공하는 함수를 호출하여 수행
        return response
    
    # GET 요청이나 다른 메소드에 대해 HttpResponseNotAllowed를 반환
    # 'POST'만 허용된다는 의미
    return HttpResponseNotAllowed(['POST'])

# 챗봇 유사답변 응답 로직
@login_required
def get_similar_answers(request, question_id):
    start_time = time.time()  # 처리 시작 시간
    username = request.user.username
    # fetch_similar_answers 함수 호출
    response = fetch_similar_answers(question_id, username)
    request_latency.labels('get_similar_answers').observe(time.time() - start_time)
    # fetch_similar_answers 함수가 JsonResponse 객체를 반환하므로,
    # 여기서는 해당 객체를 그대로 반환합니다.
    return response

# 챗봇 대화내역 출력 로직
@login_required
def get_user_chats(request):
    username = request.user.username
    chats = ChatBot.objects.filter(username=username).order_by('created_at')
    chat_data = list(chats.values('id', 'username','question', 'answer', 'created_at'))
    return JsonResponse({'chats': chat_data})

# 로그 인터랙션 로직
@csrf_exempt
def log_interaction(request):
    start_time = time.time()  # 처리 시작 시간
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
            request_latency.labels('log_interaction').observe(time.time() - start_time)
            return JsonResponse({"error": "Unsupported event type"}, status=400)

        # 성공적으로 데이터가 처리된 경우
        request_latency.labels('log_interaction').observe(time.time() - start_time)
        return JsonResponse({"status": "success"}, status=200)

    # POST 요청이 아닌 경우
    request_latency.labels('log_interaction').observe(time.time() - start_time)
    return JsonResponse({"error": "Invalid request"}, status=400)

def metrics(request):
    return HttpResponse(generate_latest(), content_type=CONTENT_TYPE_LATEST)


from django.shortcuts import render
from django.conf import settings
from django.http import JsonResponse
import requests
import os

# Create your views here.

def map(request):
    context = {'kakao_app_key': settings.KAKAO_APP_KEY}
    return render(request, 'api_app/map.html', context)

def pedia(request):
    # 지식백과 페이지에 필요한 데이터 처리
    return render(request, 'api_app/pedia.html')

def ask(request):
    # 지식백과 페이지에 필요한 데이터 처리
    return render(request, 'api_app/ask.html')

# 지식백과 api
def search_from_naver(request):
    query = request.GET.get('query', '')  # 검색어를 URL 파라미터에서 받아옵니다.
    url = "https://openapi.naver.com/v1/search/encyc.json"
    headers = {
        'X-Naver-Client-Id': os.getenv('X-Naver-Client-Id'),  # 발급받은 Client ID
        'X-Naver-Client-Secret': os.getenv('X-Naver-Client-Secret'),  # 발급받은 Client Secret
    }
    params = {
        'query': query,
        'display': 10,  # 검색 결과 출력 건수 지정
        'start': 1,  # 검색 시작 위치
    }
    
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        data = response.json()
        if not data.get('items'):  # items 키가 없거나, items 배열이 비어 있는 경우
            # 검색 결과가 없음을 알리는 메시지를 포함한 JSON 응답을 반환합니다.
            return JsonResponse({"message": "검색 결과가 없습니다."}, safe=False)
        else:
            return JsonResponse(data, safe=False)
    else:
        # 요청이 실패한 경우, 에러 메시지를 반환합니다.
        return JsonResponse({"error": "Failed to fetch data from Naver Open API"}, status=500)

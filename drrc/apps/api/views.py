from django.http import JsonResponse
from django.shortcuts import render
from langchain_google_genai import ChatGoogleGenerativeAI
from django.conf import settings


# Create your views here.
def call_llm(request):
    input_text = request.GET.get('input', '')
    llm = ChatGoogleGenerativeAI(model="gemini-pro", google_api_key=settings.GOOGLE_API_KEY)  # 모델 초기화
    result = llm.invoke(input_text) # 모델 호출
    response_data = {
        "input": input_text,
        "output": result.content
    }
    return JsonResponse(response_data)



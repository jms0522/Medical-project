from django.contrib.auth import get_user_model, authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.views.generic.edit import CreateView
from django.shortcuts import render, redirect, reverse
from django.urls import reverse_lazy

from .forms import CustomUserCreationForm, CustomAuthenticationForm
from .models import User
import os
import requests
import json

User = get_user_model()
# Create your views here.

def logout_view(request):
    logout(request)
    return redirect('chat_app:chat')

class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('chat_app:chat')
    template_name = 'common/signup.html'
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "회원가입을 축하합니다!")
        return response


class CustomLoginView(LoginView):
    authentication_form = CustomAuthenticationForm
    template_name = 'common/login.html'

def kakao_login(request):
    KAKAO_AUTH_URL = 'https://kauth.kakao.com/oauth/authorize'
    KAKAO_REDIRECT_URI='http://43.201.236.125:8000/common/kakao/login/callback'
    KAKAO_REST_API_KEY= os.getenv('KAKAO_REST_API_KEY')
    
    kakao_auth_url = f"{KAKAO_AUTH_URL}?client_id={KAKAO_REST_API_KEY}&redirect_uri={KAKAO_REDIRECT_URI}&response_type=code"
    return redirect(kakao_auth_url)

def kakao_login_callback(request):
    code = request.GET.get('code')
    KAKAO_TOKEN_URL = 'https://kauth.kakao.com/oauth/token'
    KAKAO_REDIRECT_URI='http://43.201.236.125:8000/common/kakao/login/callback'
    
    token_request = requests.post(
        KAKAO_TOKEN_URL,
        data={
            'grant_type': 'authorization_code',
            'client_id': os.getenv('KAKAO_REST_API_KEY'),
            'redirect_uri': KAKAO_REDIRECT_URI,
            'code': code,
        },
    )
    token_json = token_request.json()
    error = token_json.get('error', None)
    if error is not None:
        # 토큰 요청 실패 처리
        print("Token request failed")
        return redirect('error_page')
    
    access_token = token_json.get("access_token")
    profile_request = requests.get("https://kapi.kakao.com/v2/user/me", headers={"Authorization": f"Bearer {access_token}"})
    
    profile_json = profile_request.json()
    print(json.dumps(profile_json, indent=4, ensure_ascii=False))
    kakao_account = profile_json.get('kakao_account', {})
    email = kakao_account.get('email')
    profile = kakao_account.get('profile', {})
    nickname = profile.get('nickname', 'User')  # 기본값 'User' 설정

    if not email:
        # 이메일이 없는 경우 닉네임 기반으로 이메일 생성
        email = f"{nickname}@kakao.com"

    user, created = User.objects.get_or_create(email=email, defaults={'username': email})
    if created:
        # 신규 생성된 사용자의 경우, 추가 설정을 진행합니다.
        user.set_unusable_password()  # 소셜 로그인이므로 패스워드 설정 불필요
        user.save()

    login(request, user, backend='django.contrib.auth.backends.ModelBackend')

    # 로그인 후 리다이렉트할 페이지. 'chat_app:chat'는 예시 URL 패턴 이름입니다.
    return redirect(reverse('chat_app:chat'))

@login_required  
def profile_view(request):
    return redirect(reverse('chat_app:chat')) 

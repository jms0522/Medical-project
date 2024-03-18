from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .views import SignUpView, CustomLoginView

app_name = 'common'

urlpatterns = [
    path('login/', CustomLoginView.as_view(template_name='common/login.html'), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('signup/', SignUpView.as_view(), name='signup'),
    path('kakao/login', views.kakao_login, name='kakao_login'),
    path('kakao/login/callback', views.kakao_login_callback, name='kakao_login_callback'),
    path('profile/', views.profile_view, name='profile'),
]
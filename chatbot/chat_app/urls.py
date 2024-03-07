from django.urls import path
from . import views
from django.conf.urls.static import static
from .views import log_interaction, get_user_chats, metrics

app_name = 'chat_app'

urlpatterns = [
    path("", views.chat, name="chat"),
    path("ask_question/", views.ask_question, name="ask_question"),
    path('log_interaction/', log_interaction, name='log_interaction'),
    path('api/get_user_chats/', get_user_chats, name='get_user_chats'),
    path('metrics/', metrics),
]

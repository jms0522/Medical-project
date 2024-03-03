from django.urls import path
from . import views
from django.conf.urls.static import static
from .views import log_interaction

urlpatterns = [
    path("", views.chat, name="chat"),
    path("ask_question/", views.ask_question, name="ask_question"),
    path('log_interaction/', log_interaction, name='log_interaction'),
]

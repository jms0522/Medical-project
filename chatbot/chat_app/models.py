from django.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.models import User
class ChatBot(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)
    question = models.TextField(null=True, blank=True)
    answer = models.TextField(default='')  # 빈 문자열을 기본값으로 설정
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Chat from {self.user.username} at {self.created_at}"
    
class UserInteractionLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    event_type = models.CharField(max_length=100)
    element_id = models.CharField(max_length=255, null=True, blank=True)
    element_class = models.CharField(max_length=255, null=True, blank=True)
    element_type = models.CharField(max_length=255, null=True, blank=True)
    element_name = models.CharField(max_length=255, null=True, blank=True)
    url = models.URLField(null=True)
    timestamp = models.DateTimeField()

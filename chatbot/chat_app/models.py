from django.db import models
from django.conf import settings
from django.utils import timezone

class ChatBot(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    question = models.TextField(null=True, blank=True)
    answer = models.TextField(default='')  # 빈 문자열을 기본값으로 설정
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Chat from {self.user.username} at {self.created_at}"
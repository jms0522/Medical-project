from django.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.models import User
class ChatBot(models.Model):
    username = models.CharField(max_length=150, null=True, blank=True)
    question = models.TextField(null=True, blank=True)
    answer = models.TextField(default='')  # 빈 문자열을 기본값으로 설정
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Chat from {self.user.username} at {self.created_at}"
    
class UserInteractionLog(models.Model):
    username = models.CharField(max_length=150, null=True, blank=True)
    event_type = models.CharField(max_length=100)
    element_id = models.CharField(max_length=255, null=True, blank=True)
    element_class = models.CharField(max_length=255, null=True, blank=True)
    element_type = models.CharField(max_length=255, null=True, blank=True)
    element_name = models.CharField(max_length=255, null=True, blank=True)
    url = models.URLField(null=True)
    timestamp = models.DateTimeField()
    
    
class SimilarAnswer(models.Model):
    original_question = models.ForeignKey(ChatBot, on_delete=models.CASCADE, related_name='similar_answers')
    similar_question = models.TextField(null=True, blank=True)
    similar_answer = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Similar answer to question ID {self.original_question.id} created at {self.created_at}"
    
class ClickEventLog(models.Model):
    username = models.CharField(max_length=150, null=True, blank=True)
    element_class = models.CharField(max_length=255, null=True, blank=True)
    element_name = models.CharField(max_length=255, null=True, blank=True)
    url = models.URLField()
    timestamp = models.DateTimeField()


class FormSubmitEventLog(models.Model):
    username = models.CharField(max_length=150, null=True, blank=True)
    element_class = models.CharField(max_length=255, null=True, blank=True)
    element_name = models.CharField(max_length=255, null=True, blank=True)
    url = models.URLField()
    timestamp = models.DateTimeField()


class ScrollEventLog(models.Model):
    username = models.CharField(max_length=150, null=True, blank=True)
    element_class = models.CharField(max_length=255, null=True, blank=True)
    element_name = models.CharField(max_length=255, null=True, blank=True)
    url = models.URLField()
    scrollPosition = models.IntegerField(null=True, blank=True)  # 스크롤 위치 저장
    timestamp = models.DateTimeField()


class PageViewEventLog(models.Model):
    username = models.CharField(max_length=150, null=True, blank=True)
    element_class = models.CharField(max_length=255, null=True, blank=True)
    element_name = models.CharField(max_length=255, null=True, blank=True)
    url = models.URLField()
    timestamp = models.DateTimeField()


class ErrorLog(models.Model):
    username = models.CharField(max_length=150, null=True, blank=True)
    element_class = models.CharField(max_length=255, null=True, blank=True)
    element_name = models.CharField(max_length=255, null=True, blank=True)
    url = models.URLField()
    message = models.CharField(max_length=255, null=True, blank=True)  # 에러 메시지 저장
    lineno = models.IntegerField(null=True, blank=True)  # 줄 번호
    timestamp = models.DateTimeField()



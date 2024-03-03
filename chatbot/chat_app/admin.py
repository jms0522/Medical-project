from django.contrib import admin
from .models import UserInteractionLog

@admin.register(UserInteractionLog)
class UserInteractionLogAdmin(admin.ModelAdmin):
    list_display = ['event_type', 'element_id', 'element_class', 'element_type', 'element_name', 'url', 'timestamp', 'user']

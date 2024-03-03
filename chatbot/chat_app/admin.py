from django.contrib import admin
from .models import UserInteractionLog

@admin.register(UserInteractionLog)
class UserInteractionLogAdmin(admin.ModelAdmin):
    list_display = ['get_username', 'event_type', 'element_id', 'element_class', 'element_type', 'element_name', 'url', 'timestamp']
    
    def get_username(self, obj):
        return obj.user.username if obj.user else '비로그인 사용자'
    get_username.short_description = '사용자 이름'  # Admin 사이트에 표시될 컬럼 이름

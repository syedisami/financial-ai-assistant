from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Log


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """Admin interface for CustomUser"""
    list_display = ('username', 'email', 'role', 'is_staff', 'is_active', 'date_joined')
    list_filter = ('role', 'is_staff', 'is_active', 'date_joined')
    search_fields = ('username', 'email')
    
    fieldsets = UserAdmin.fieldsets + (
        ('Role Information', {'fields': ('role',)}),
    )


@admin.register(Log)
class LogAdmin(admin.ModelAdmin):
    """Admin interface for chat logs"""
    list_display = ('user', 'question_preview', 'timestamp')
    list_filter = ('timestamp', 'user')
    search_fields = ('question', 'answer', 'user__username')
    readonly_fields = ('timestamp',)
    
    def question_preview(self, obj):
        return obj.question[:50] + '...' if len(obj.question) > 50 else obj.question
    question_preview.short_description = 'Question'

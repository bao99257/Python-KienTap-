from django.contrib import admin
from .models import ChatSession, ChatMessage, ChatBotConfig

# Register your models here.

@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'title', 'created_at', 'updated_at', 'is_active']
    list_filter = ['is_active', 'created_at', 'updated_at']
    search_fields = ['user__username', 'title']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-updated_at']

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'session', 'role', 'content_preview', 'timestamp', 'model_used']
    list_filter = ['role', 'timestamp', 'model_used']
    search_fields = ['session__title', 'content']
    readonly_fields = ['timestamp']
    ordering = ['-timestamp']

    def content_preview(self, obj):
        return obj.content[:100] + "..." if len(obj.content) > 100 else obj.content
    content_preview.short_description = 'Content Preview'

@admin.register(ChatBotConfig)
class ChatBotConfigAdmin(admin.ModelAdmin):
    list_display = ['user', 'default_model', 'temperature', 'max_tokens', 'created_at', 'updated_at']
    list_filter = ['default_model', 'created_at']
    search_fields = ['user__username']
    readonly_fields = ['created_at', 'updated_at']

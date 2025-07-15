from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.

class ChatSession(models.Model):
    """Model để lưu trữ phiên chat"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_sessions')
    title = models.CharField(max_length=200, default="New Chat")
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.user.username} - {self.title}"

class ChatMessage(models.Model):
    """Model để lưu trữ tin nhắn trong chat"""
    ROLE_CHOICES = [
        ('user', 'User'),
        ('assistant', 'Assistant'),
        ('system', 'System'),
    ]

    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    content = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    model_used = models.CharField(max_length=100, blank=True, null=True)  # Tên model AI được sử dụng

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"{self.session.title} - {self.role}: {self.content[:50]}..."

class ChatBotConfig(models.Model):
    """Model để lưu trữ cấu hình chatbot"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='chatbot_config')
    default_model = models.CharField(max_length=100, default='llama3.2:3b')
    system_prompt = models.TextField(
        default="You are a helpful AI assistant. Please provide accurate and helpful responses."
    )
    temperature = models.FloatField(default=0.7)  # Độ sáng tạo của AI
    max_tokens = models.IntegerField(default=1000)  # Số token tối đa trong phản hồi
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - Config"

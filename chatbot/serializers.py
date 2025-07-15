from rest_framework import serializers
from .models import ChatSession, ChatMessage, ChatBotConfig
from django.contrib.auth.models import User

class ChatMessageSerializer(serializers.ModelSerializer):
    """Serializer cho ChatMessage"""
    class Meta:
        model = ChatMessage
        fields = ['id', 'role', 'content', 'timestamp', 'model_used']
        read_only_fields = ['id', 'timestamp']

class ChatSessionSerializer(serializers.ModelSerializer):
    """Serializer cho ChatSession"""
    messages = ChatMessageSerializer(many=True, read_only=True)
    message_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ChatSession
        fields = ['id', 'title', 'created_at', 'updated_at', 'is_active', 'messages', 'message_count']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_message_count(self, obj):
        return obj.messages.count()

class ChatSessionListSerializer(serializers.ModelSerializer):
    """Serializer cho danh sách ChatSession (không bao gồm messages)"""
    message_count = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()
    
    class Meta:
        model = ChatSession
        fields = ['id', 'title', 'created_at', 'updated_at', 'is_active', 'message_count', 'last_message']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_message_count(self, obj):
        return obj.messages.count()
    
    def get_last_message(self, obj):
        last_message = obj.messages.last()
        if last_message:
            return {
                'content': last_message.content[:100] + '...' if len(last_message.content) > 100 else last_message.content,
                'role': last_message.role,
                'timestamp': last_message.timestamp
            }
        return None

class ChatBotConfigSerializer(serializers.ModelSerializer):
    """Serializer cho ChatBotConfig"""
    class Meta:
        model = ChatBotConfig
        fields = ['default_model', 'system_prompt', 'temperature', 'max_tokens', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

class ChatRequestSerializer(serializers.Serializer):
    """Serializer cho request gửi tin nhắn chat"""
    message = serializers.CharField(max_length=5000)
    session_id = serializers.IntegerField(required=False)
    model = serializers.CharField(max_length=100, required=False)
    temperature = serializers.FloatField(min_value=0.0, max_value=2.0, required=False)
    
    def validate_message(self, value):
        if not value.strip():
            raise serializers.ValidationError("Message cannot be empty")
        return value.strip()

class ChatResponseSerializer(serializers.Serializer):
    """Serializer cho response của chat"""
    message = serializers.CharField()
    session_id = serializers.IntegerField()
    model_used = serializers.CharField()
    timestamp = serializers.DateTimeField()
    
class ModelListSerializer(serializers.Serializer):
    """Serializer cho danh sách models có sẵn"""
    name = serializers.CharField()
    size = serializers.CharField(required=False)
    modified_at = serializers.DateTimeField(required=False)

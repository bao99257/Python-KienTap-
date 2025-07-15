from django.shortcuts import render, get_object_or_404
from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import User
from django.utils import timezone
import ollama
import json
import logging

from .models import ChatSession, ChatMessage, ChatBotConfig
from .serializers import (
    ChatSessionSerializer, ChatSessionListSerializer,
    ChatMessageSerializer, ChatBotConfigSerializer,
    ChatRequestSerializer, ChatResponseSerializer,
    ModelListSerializer
)
from .services import SmartChatbotService

# Create your views here.

logger = logging.getLogger(__name__)

class ChatSessionListCreateView(generics.ListCreateAPIView):
    """API để lấy danh sách và tạo chat session mới"""
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ChatSessionListSerializer
        return ChatSessionSerializer

    def get_queryset(self):
        return ChatSession.objects.filter(user=self.request.user, is_active=True)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class ChatSessionDetailView(generics.RetrieveUpdateDestroyAPIView):
    """API để lấy chi tiết, cập nhật và xóa chat session"""
    serializer_class = ChatSessionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ChatSession.objects.filter(user=self.request.user)

    def perform_destroy(self, instance):
        # Soft delete
        instance.is_active = False
        instance.save()

class ChatBotConfigView(APIView):
    """API để lấy và cập nhật cấu hình chatbot"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        config, created = ChatBotConfig.objects.get_or_create(user=request.user)
        serializer = ChatBotConfigSerializer(config)
        return Response(serializer.data)

    def put(self, request):
        config, created = ChatBotConfig.objects.get_or_create(user=request.user)
        serializer = ChatBotConfigSerializer(config, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ChatView(APIView):
    """API chính để chat với AI - Smart Chatbot"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ChatRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        message = serializer.validated_data['message']
        session_id = serializer.validated_data.get('session_id')
        model = serializer.validated_data.get('model')
        temperature = serializer.validated_data.get('temperature')

        try:
            # Lấy hoặc tạo session
            if session_id:
                session = get_object_or_404(ChatSession, id=session_id, user=request.user)
            else:
                session = ChatSession.objects.create(
                    user=request.user,
                    title=message[:50] + "..." if len(message) > 50 else message
                )

            # Lấy cấu hình user
            config, _ = ChatBotConfig.objects.get_or_create(user=request.user)
            model_to_use = model or config.default_model

            # Lưu tin nhắn của user
            user_message = ChatMessage.objects.create(
                session=session,
                role='user',
                content=message
            )

            # Sử dụng SmartChatbotService để xử lý tin nhắn
            chatbot_service = SmartChatbotService(request.user)
            result = chatbot_service.process_message(message, model_to_use)

            # Xử lý kết quả từ service
            if result['type'] == 'product_list':
                ai_response = result['message']
                response_data = {
                    'message': ai_response,
                    'session_id': session.id,
                    'model_used': model_to_use,
                    'type': 'product_list',
                    'products': result['products'],
                    'count': result['count']
                }

            elif result['type'] == 'order_list':
                ai_response = result['message']
                response_data = {
                    'message': ai_response,
                    'session_id': session.id,
                    'model_used': model_to_use,
                    'type': 'order_list',
                    'orders': result['orders'],
                    'count': result['count']
                }

            elif result['type'] == 'favorite_list':
                ai_response = result['message']
                response_data = {
                    'message': ai_response,
                    'session_id': session.id,
                    'model_used': model_to_use,
                    'type': 'favorite_list',
                    'products': result['products'],
                    'count': result['count']
                }

            else:  # general_response, no_products, no_orders, no_favorites, error
                ai_response = result['message']
                response_data = {
                    'message': ai_response,
                    'session_id': session.id,
                    'model_used': model_to_use,
                    'type': result['type']
                }

            # Lưu phản hồi của AI
            ai_message = ChatMessage.objects.create(
                session=session,
                role='assistant',
                content=ai_response,
                model_used=model_to_use
            )

            # Cập nhật thời gian session
            session.updated_at = timezone.now()
            session.save()

            response_data['timestamp'] = ai_message.timestamp
            return Response(response_data)

        except Exception as e:
            logger.error(f"Smart Chat error: {str(e)}")
            return Response({
                'error': f'Internal server error: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_available_models(request):
    """API để lấy danh sách models có sẵn từ Ollama"""
    try:
        models_response = ollama.list()
        logger.info(f"Ollama models response: {models_response}")

        model_list = []
        models = models_response.get('models', [])

        for model in models:
            # Handle different possible response structures
            if hasattr(model, 'name'):
                # New Ollama version with model objects
                name = model.name
                size = getattr(model, 'size', 'Unknown')
                modified_at = getattr(model, 'modified_at', None)
            elif isinstance(model, dict):
                name = model.get('name') or model.get('model') or str(model)
                size = model.get('size', 'Unknown')
                modified_at = model.get('modified_at')
            else:
                # If model is just a string or other object
                name = str(model).split("'")[1] if "'" in str(model) else str(model)
                size = 'Unknown'
                modified_at = None

            model_list.append({
                'name': name,
                'size': size,
                'modified_at': modified_at
            })

        # If no models found, provide default models
        if not model_list:
            model_list = [
                {'name': 'llama3.2', 'size': 'Unknown', 'modified_at': None},
                {'name': 'llama3.2:1b', 'size': 'Unknown', 'modified_at': None},
                {'name': 'llama3.2:3b', 'size': 'Unknown', 'modified_at': None},
            ]

        serializer = ModelListSerializer(model_list, many=True)
        return Response(serializer.data)
    except Exception as e:
        logger.error(f"Error getting models: {str(e)}")
        # Return default models on error
        default_models = [
            {'name': 'llama3.2', 'size': 'Unknown', 'modified_at': None},
            {'name': 'llama3.2:1b', 'size': 'Unknown', 'modified_at': None},
            {'name': 'llama3.2:3b', 'size': 'Unknown', 'modified_at': None},
        ]
        serializer = ModelListSerializer(default_models, many=True)
        return Response(serializer.data)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def pull_model(request):
    """API để tải model mới từ Ollama"""
    model_name = request.data.get('model_name')
    if not model_name:
        return Response({
            'error': 'model_name is required'
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Gọi Ollama để pull model
        ollama.pull(model_name)
        return Response({
            'message': f'Model {model_name} pulled successfully'
        })
    except Exception as e:
        logger.error(f"Error pulling model {model_name}: {str(e)}")
        return Response({
            'error': f'Could not pull model: {str(e)}'
        }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def delete_session_messages(request, session_id):
    """API để xóa tất cả tin nhắn trong một session"""
    try:
        session = get_object_or_404(ChatSession, id=session_id, user=request.user)
        session.messages.all().delete()
        return Response({
            'message': 'All messages deleted successfully'
        })
    except Exception as e:
        logger.error(f"Error deleting messages: {str(e)}")
        return Response({
            'error': f'Could not delete messages: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

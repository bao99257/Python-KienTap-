import json
import asyncio
import logging
from decimal import Decimal
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.utils import timezone
import ollama

from .models import ChatSession, ChatMessage, ChatBotConfig
from .services import SmartChatbotService

User = get_user_model()
logger = logging.getLogger(__name__)

class DecimalEncoder(json.JSONEncoder):
    """Custom JSON encoder để handle Decimal"""
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)

class ChatBotConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        if self.user.is_anonymous:
            await self.close()
            return
        
        self.session_id = self.scope['url_route']['kwargs']['session_id']
        self.room_group_name = f'chatbot_{self.user.id}_{self.session_id}'
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message_type = data.get('type', 'chat_message')
            
            if message_type == 'chat_message':
                await self.handle_chat_message(data)
            elif message_type == 'typing':
                await self.handle_typing(data)
                
        except Exception as e:
            logger.error(f"Error in receive: {str(e)}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': f'Error processing message: {str(e)}'
            }, cls=DecimalEncoder))

    async def handle_chat_message(self, data):
        message = data.get('message', '').strip()
        if not message:
            return

        model = data.get('model')

        try:
            # Get or create session
            session = await self.get_or_create_session()

            # Get user config
            config = await self.get_user_config()
            model_to_use = model or config.default_model

            # Save user message
            user_message = await self.save_message(
                session, 'user', message
            )

            # Send user message to group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message_broadcast',
                    'message': {
                        'id': user_message.id,
                        'role': 'user',
                        'content': message,
                        'timestamp': user_message.timestamp.isoformat(),
                    }
                }
            )

            # Send typing indicator
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'typing_broadcast',
                    'typing': True
                }
            )

            # Use SmartChatbotService to process message
            result = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: SmartChatbotService(self.user).process_message(message, model_to_use)
            )

            # Process result and send response
            await self.send_smart_response(session, result, model_to_use)

        except Exception as e:
            logger.error(f"Error handling chat message: {str(e)}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': f'Error: {str(e)}'
            }, cls=DecimalEncoder))

    async def send_smart_response(self, session, result, model_to_use):
        """Send smart response based on result type"""
        try:
            ai_response = result['message']

            # Save AI message
            ai_message = await self.save_message(
                session, 'assistant', ai_response, model_to_use
            )

            # Stop typing indicator
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'typing_broadcast',
                    'typing': False
                }
            )

            # Prepare response data
            response_data = {
                'type': 'message',
                'message': {
                    'id': ai_message.id,
                    'role': 'assistant',
                    'content': ai_response,
                    'timestamp': ai_message.timestamp.isoformat(),
                    'model_used': model_to_use,
                    'response_type': result['type']
                }
            }

            # Add extra data based on response type
            if result['type'] == 'product_list':
                response_data['message']['products'] = result['products']
                response_data['message']['count'] = result['count']
            elif result['type'] == 'order_list':
                response_data['message']['orders'] = result['orders']
                response_data['message']['count'] = result['count']
            elif result['type'] == 'favorite_list':
                response_data['message']['products'] = result['products']
                response_data['message']['count'] = result['count']

            # Send to group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message_broadcast',
                    'message': response_data['message']
                }
            )

        except Exception as e:
            logger.error(f"Error sending smart response: {str(e)}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': f'Error sending response: {str(e)}'
            }, cls=DecimalEncoder))

    async def generate_ai_response_stream(self, session, messages_history, model, temperature, config):
        try:
            # Call Ollama with streaming
            response_content = ""
            
            # For now, we'll use the regular chat method and simulate streaming
            # In a real implementation, you might want to use ollama's streaming capabilities
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: ollama.chat(
                    model=model,
                    messages=messages_history,
                    options={
                        'temperature': temperature,
                        'num_predict': config.max_tokens
                    }
                )
            )
            
            response_content = response['message']['content']
            
            # Stop typing indicator
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'typing_broadcast',
                    'typing': False
                }
            )
            
            # Save AI response
            ai_message = await self.save_message(
                session, 'assistant', response_content, model
            )
            
            # Send complete AI response
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message_broadcast',
                    'message': {
                        'id': ai_message.id,
                        'role': 'assistant',
                        'content': response_content,
                        'timestamp': ai_message.timestamp.isoformat(),
                        'model_used': model,
                    }
                }
            )
            
            # Update session timestamp
            await self.update_session_timestamp(session)
            
        except Exception as e:
            logger.error(f"Error generating AI response: {str(e)}")
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'typing_broadcast',
                    'typing': False
                }
            )
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': f'AI service error: {str(e)}'
            }, cls=DecimalEncoder))

    async def handle_typing(self, data):
        typing = data.get('typing', False)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'typing_broadcast',
                'typing': typing,
                'user_id': self.user.id
            }
        )

    # WebSocket message handlers
    async def chat_message_broadcast(self, event):
        await self.send(text_data=json.dumps({
            'type': 'message',
            'message': event['message']
        }, cls=DecimalEncoder))

    async def typing_broadcast(self, event):
        await self.send(text_data=json.dumps({
            'type': 'typing',
            'typing': event['typing'],
            'user_id': event.get('user_id')
        }, cls=DecimalEncoder))

    # Database operations
    @database_sync_to_async
    def get_or_create_session(self):
        session, created = ChatSession.objects.get_or_create(
            id=self.session_id,
            user=self.user,
            defaults={'title': 'New Chat'}
        )
        return session

    @database_sync_to_async
    def get_user_config(self):
        config, created = ChatBotConfig.objects.get_or_create(user=self.user)
        return config

    @database_sync_to_async
    def save_message(self, session, role, content, model_used=None):
        return ChatMessage.objects.create(
            session=session,
            role=role,
            content=content,
            model_used=model_used
        )

    @database_sync_to_async
    def get_chat_history(self, session, config):
        messages_history = []
        
        # Add system prompt if exists
        if config.system_prompt:
            messages_history.append({
                'role': 'system',
                'content': config.system_prompt
            })
        
        # Add recent messages (last 10)
        recent_messages = list(session.messages.order_by('timestamp')[-10:])
        for msg in recent_messages:
            messages_history.append({
                'role': msg.role,
                'content': msg.content
            })
        
        return messages_history

    @database_sync_to_async
    def update_session_timestamp(self, session):
        session.updated_at = timezone.now()
        session.save()

from django.urls import path
from . import views

app_name = 'chatbot'

urlpatterns = [
    # Chat sessions
    path('sessions/', views.ChatSessionListCreateView.as_view(), name='session-list-create'),
    path('sessions/<int:pk>/', views.ChatSessionDetailView.as_view(), name='session-detail'),
    path('sessions/<int:session_id>/messages/', views.delete_session_messages, name='delete-session-messages'),
    
    # Chat API
    path('chat/', views.ChatView.as_view(), name='chat'),
    
    # Configuration
    path('config/', views.ChatBotConfigView.as_view(), name='config'),
    
    # Models
    path('models/', views.get_available_models, name='available-models'),
    path('models/pull/', views.pull_model, name='pull-model'),
]

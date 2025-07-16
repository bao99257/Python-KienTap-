"""
Context Memory System for Chatbot
Manages conversation context, user preferences, and session state
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from django.core.cache import cache
from django.contrib.auth.models import User

logger = logging.getLogger(__name__)

@dataclass
class UserPreference:
    """Sở thích người dùng"""
    preferred_categories: List[str]
    preferred_brands: List[str]
    preferred_price_range: Dict[str, int]  # {'min': 100000, 'max': 500000}
    preferred_sizes: List[str]
    preferred_colors: List[str]
    style_preferences: List[str]  # ['casual', 'formal', 'sporty']
    
@dataclass
class ConversationTurn:
    """Một lượt hội thoại"""
    timestamp: datetime
    user_message: str
    bot_response: str
    intent: str
    entities: Dict[str, Any]
    user_satisfaction: Optional[int] = None  # 1-5 rating
    
@dataclass
class SessionContext:
    """Context của một phiên chat"""
    session_id: str
    user_id: Optional[int]
    start_time: datetime
    last_activity: datetime
    conversation_history: List[ConversationTurn]
    current_topic: Optional[str]
    pending_questions: List[str]
    user_preferences: Optional[UserPreference]
    temporary_data: Dict[str, Any]  # Dữ liệu tạm thời trong phiên
    
class ContextManager:
    """Quản lý context và memory cho chatbot"""
    
    def __init__(self):
        self.session_timeout = 3600  # 1 hour
        self.max_history_length = 20
        
    def get_session_key(self, session_id: str) -> str:
        """Tạo cache key cho session"""
        return f"chat_session_{session_id}"
    
    def get_user_pref_key(self, user_id: int) -> str:
        """Tạo cache key cho user preferences"""
        return f"user_preferences_{user_id}"
    
    def create_session(self, session_id: str, user_id: Optional[int] = None) -> SessionContext:
        """Tạo session mới"""
        now = datetime.now()
        
        # Load user preferences if available
        user_preferences = None
        if user_id:
            user_preferences = self.get_user_preferences(user_id)
        
        session = SessionContext(
            session_id=session_id,
            user_id=user_id,
            start_time=now,
            last_activity=now,
            conversation_history=[],
            current_topic=None,
            pending_questions=[],
            user_preferences=user_preferences,
            temporary_data={}
        )
        
        self.save_session(session)
        return session
    
    def get_session(self, session_id: str) -> Optional[SessionContext]:
        """Lấy session từ cache"""
        cache_key = self.get_session_key(session_id)
        session_data = cache.get(cache_key)
        
        if not session_data:
            return None
        
        try:
            # Deserialize session data
            session = SessionContext(**session_data)
            
            # Check if session expired
            if datetime.now() - session.last_activity > timedelta(seconds=self.session_timeout):
                self.delete_session(session_id)
                return None
            
            return session
        except Exception as e:
            logger.error(f"Error deserializing session {session_id}: {e}")
            return None
    
    def save_session(self, session: SessionContext):
        """Lưu session vào cache"""
        cache_key = self.get_session_key(session.session_id)
        session_data = asdict(session)
        
        # Convert datetime objects to strings for JSON serialization
        session_data['start_time'] = session.start_time.isoformat()
        session_data['last_activity'] = session.last_activity.isoformat()
        
        # Convert conversation history
        for turn in session_data['conversation_history']:
            turn['timestamp'] = turn['timestamp'].isoformat() if isinstance(turn['timestamp'], datetime) else turn['timestamp']
        
        cache.set(cache_key, session_data, timeout=self.session_timeout)
    
    def delete_session(self, session_id: str):
        """Xóa session"""
        cache_key = self.get_session_key(session_id)
        cache.delete(cache_key)
    
    def add_conversation_turn(self, session_id: str, user_message: str, 
                           bot_response: str, intent: str, entities: Dict[str, Any]):
        """Thêm lượt hội thoại mới"""
        session = self.get_session(session_id)
        if not session:
            return
        
        turn = ConversationTurn(
            timestamp=datetime.now(),
            user_message=user_message,
            bot_response=bot_response,
            intent=intent,
            entities=entities
        )
        
        session.conversation_history.append(turn)
        session.last_activity = datetime.now()
        
        # Limit history length
        if len(session.conversation_history) > self.max_history_length:
            session.conversation_history = session.conversation_history[-self.max_history_length:]
        
        self.save_session(session)
    
    def get_conversation_context(self, session_id: str, last_n: int = 5) -> List[Dict[str, Any]]:
        """Lấy context hội thoại gần đây"""
        session = self.get_session(session_id)
        if not session:
            return []
        
        recent_turns = session.conversation_history[-last_n:]
        return [
            {
                'user_message': turn.user_message,
                'bot_response': turn.bot_response,
                'intent': turn.intent,
                'entities': turn.entities,
                'timestamp': turn.timestamp.isoformat() if isinstance(turn.timestamp, datetime) else turn.timestamp
            }
            for turn in recent_turns
        ]
    
    def update_current_topic(self, session_id: str, topic: str):
        """Cập nhật chủ đề hiện tại"""
        session = self.get_session(session_id)
        if session:
            session.current_topic = topic
            session.last_activity = datetime.now()
            self.save_session(session)
    
    def add_pending_question(self, session_id: str, question: str):
        """Thêm câu hỏi chờ xử lý"""
        session = self.get_session(session_id)
        if session:
            session.pending_questions.append(question)
            self.save_session(session)
    
    def get_pending_questions(self, session_id: str) -> List[str]:
        """Lấy danh sách câu hỏi chờ xử lý"""
        session = self.get_session(session_id)
        return session.pending_questions if session else []
    
    def clear_pending_questions(self, session_id: str):
        """Xóa câu hỏi chờ xử lý"""
        session = self.get_session(session_id)
        if session:
            session.pending_questions = []
            self.save_session(session)
    
    def set_temporary_data(self, session_id: str, key: str, value: Any):
        """Lưu dữ liệu tạm thời"""
        session = self.get_session(session_id)
        if session:
            session.temporary_data[key] = value
            self.save_session(session)
    
    def get_temporary_data(self, session_id: str, key: str, default: Any = None) -> Any:
        """Lấy dữ liệu tạm thời"""
        session = self.get_session(session_id)
        if session:
            return session.temporary_data.get(key, default)
        return default
    
    def get_user_preferences(self, user_id: int) -> Optional[UserPreference]:
        """Lấy sở thích người dùng"""
        cache_key = self.get_user_pref_key(user_id)
        pref_data = cache.get(cache_key)
        
        if pref_data:
            try:
                return UserPreference(**pref_data)
            except Exception as e:
                logger.error(f"Error deserializing user preferences {user_id}: {e}")
        
        # Load from database or create default
        return self._create_default_preferences()
    
    def save_user_preferences(self, user_id: int, preferences: UserPreference):
        """Lưu sở thích người dùng"""
        cache_key = self.get_user_pref_key(user_id)
        pref_data = asdict(preferences)
        cache.set(cache_key, pref_data, timeout=86400)  # 24 hours
    
    def update_user_preferences_from_interaction(self, session_id: str, entities: Dict[str, Any]):
        """Cập nhật sở thích từ tương tác"""
        session = self.get_session(session_id)
        if not session or not session.user_id:
            return
        
        preferences = session.user_preferences or self._create_default_preferences()
        
        # Update preferences based on entities
        if 'product_type' in entities:
            for product_type in entities['product_type']:
                if product_type not in preferences.preferred_categories:
                    preferences.preferred_categories.append(product_type)
        
        if 'brand' in entities:
            for brand in entities['brand']:
                if brand not in preferences.preferred_brands:
                    preferences.preferred_brands.append(brand)
        
        if 'size' in entities:
            for size in entities['size']:
                if size not in preferences.preferred_sizes:
                    preferences.preferred_sizes.append(size)
        
        if 'color' in entities:
            for color in entities['color']:
                if color not in preferences.preferred_colors:
                    preferences.preferred_colors.append(color)
        
        # Update session and save
        session.user_preferences = preferences
        self.save_session(session)
        self.save_user_preferences(session.user_id, preferences)
    
    def _create_default_preferences(self) -> UserPreference:
        """Tạo sở thích mặc định"""
        return UserPreference(
            preferred_categories=[],
            preferred_brands=[],
            preferred_price_range={'min': 0, 'max': 1000000},
            preferred_sizes=[],
            preferred_colors=[],
            style_preferences=[]
        )
    
    def get_session_summary(self, session_id: str) -> Dict[str, Any]:
        """Lấy tóm tắt session"""
        session = self.get_session(session_id)
        if not session:
            return {}
        
        return {
            'session_id': session.session_id,
            'user_id': session.user_id,
            'duration': (datetime.now() - session.start_time).total_seconds(),
            'message_count': len(session.conversation_history),
            'current_topic': session.current_topic,
            'pending_questions_count': len(session.pending_questions),
            'last_activity': session.last_activity.isoformat()
        }

# Global instance
context_manager = ContextManager()

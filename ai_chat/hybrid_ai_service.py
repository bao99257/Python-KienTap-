"""
Hybrid AI Service - Production Ready Chatbot Service
Combines reliable core logic with Gemini AI enhancement
"""

import logging
from typing import Dict, List, Optional
from .hybrid_chatbot import HybridChatbot

logger = logging.getLogger(__name__)


class HybridAIService:
    """Production-ready Hybrid AI Service"""
    
    def __init__(self):
        self.chatbot = HybridChatbot()
    
    def process_message(self, message: str, user=None, session_id=None) -> Dict:
        """
        Process message using hybrid approach
        Returns standardized response format for views.py
        """
        try:
            # Use hybrid chatbot to process message
            result = self.chatbot.process_message(message, user, session_id)
            
            # Ensure response format matches what views.py expects
            if isinstance(result, dict) and 'message' in result:
                return result
            else:
                # Fallback format
                return {
                    'message': str(result) if result else "Xin lỗi, tôi không hiểu câu hỏi của bạn.",
                    'actions_taken': [],
                    'suggested_products': [],
                    'quick_replies': [],
                    'metadata': {}
                }
                
        except Exception as e:
            logger.error(f"Error in HybridAIService: {e}")
            return {
                'message': "Xin lỗi, có lỗi xảy ra. Vui lòng thử lại sau.",
                'actions_taken': [],
                'suggested_products': [],
                'quick_replies': [],
                'metadata': {'error': str(e)}
            }


# Global instance
hybrid_ai_service = HybridAIService()

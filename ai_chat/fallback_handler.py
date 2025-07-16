"""
Advanced Fallback Handler for Chatbot
Handles unclear intents, provides smart suggestions, and manages conversation flow
"""

import random
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from .intent_detector import IntentType, IntentResult
from .context_manager import context_manager

logger = logging.getLogger(__name__)

@dataclass
class FallbackResponse:
    """Response từ fallback handler"""
    message: str
    suggestions: List[str]
    clarification_needed: bool
    escalate_to_human: bool
    confidence_boost_tips: List[str]

class FallbackHandler:
    """Xử lý các trường hợp bot không hiểu hoặc không chắc chắn"""
    
    def __init__(self):
        self.clarification_templates = self._build_clarification_templates()
        self.suggestion_templates = self._build_suggestion_templates()
        self.escalation_triggers = self._build_escalation_triggers()
        
    def _build_clarification_templates(self) -> Dict[str, List[str]]:
        """Templates để hỏi làm rõ"""
        return {
            'product_search_unclear': [
                "Bạn đang tìm loại sản phẩm nào cụ thể? Ví dụ: áo thun, quần jean, giày thể thao...",
                "Mình chưa hiểu rõ bạn muốn tìm gì. Bạn có thể mô tả chi tiết hơn không?",
                "Để tìm được sản phẩm phù hợp, bạn có thể cho mình biết: loại sản phẩm, size, màu sắc, giá cả?",
            ],
            'price_unclear': [
                "Bạn muốn hỏi giá sản phẩm nào? Hoặc đang tìm sản phẩm trong tầm giá bao nhiêu?",
                "Mình cần biết tên sản phẩm để check giá cho bạn nhé!",
                "Bạn có thể nói rõ hơn về sản phẩm và mức giá mong muốn không?",
            ],
            'size_unclear': [
                "Bạn cần tư vấn size cho sản phẩm nào? Và hiện tại bạn mặc size gì?",
                "Để tư vấn size chính xác, bạn có thể cho mình biết chiều cao, cân nặng không?",
                "Size nào bạn đang quan tâm? S, M, L hay size số?",
            ],
            'general_unclear': [
                "Mình chưa hiểu rõ ý bạn. Bạn có thể nói lại bằng cách khác không?",
                "Bạn có thể mô tả chi tiết hơn để mình hỗ trợ tốt hơn?",
                "Xin lỗi, mình chưa nắm được ý bạn. Bạn cần hỗ trợ gì cụ thể?",
            ]
        }
    
    def _build_suggestion_templates(self) -> Dict[str, List[str]]:
        """Templates gợi ý hành động"""
        return {
            'product_suggestions': [
                "🛍️ Tìm sản phẩm theo danh mục",
                "💰 Xem sản phẩm theo giá",
                "🔥 Sản phẩm hot nhất",
                "🆕 Sản phẩm mới nhất",
                "💎 Sản phẩm cao cấp",
                "🏷️ Sản phẩm giảm giá",
            ],
            'service_suggestions': [
                "📏 Tư vấn size",
                "🚚 Thông tin vận chuyển",
                "🔄 Chính sách đổi trả",
                "💳 Hướng dẫn thanh toán",
                "📞 Liên hệ tư vấn viên",
                "❓ Câu hỏi thường gặp",
            ],
            'general_suggestions': [
                "Tìm sản phẩm",
                "Hỏi giá",
                "Check size",
                "Xem khuyến mãi",
                "Chính sách shop",
                "Liên hệ hỗ trợ",
            ]
        }
    
    def _build_escalation_triggers(self) -> List[str]:
        """Các trigger để chuyển lên human"""
        return [
            'không hài lòng', 'thất vọng', 'tệ', 'dở', 'kém',
            'khiếu nại', 'phàn nàn', 'complain', 'manager',
            'giám đốc', 'sếp', 'người phụ trách',
            'không giải quyết được', 'không hỗ trợ được',
            'muốn nói chuyện với người thật',
        ]
    
    def handle_low_confidence_intent(self, intent_result: IntentResult, 
                                   user_message: str, session_id: str) -> FallbackResponse:
        """Xử lý intent có confidence thấp"""
        
        # Lấy context để hiểu rõ hơn
        context = context_manager.get_conversation_context(session_id, last_n=3)
        
        # Kiểm tra có cần escalate không
        if self._should_escalate(user_message):
            return self._create_escalation_response()
        
        # Xử lý theo loại intent
        if intent_result.intent == IntentType.PRODUCT_SEARCH:
            return self._handle_unclear_product_search(intent_result, context)
        elif intent_result.intent == IntentType.PRICE_INQUIRY:
            return self._handle_unclear_price_inquiry(intent_result, context)
        elif intent_result.intent == IntentType.SIZE_INQUIRY:
            return self._handle_unclear_size_inquiry(intent_result, context)
        else:
            return self._handle_general_unclear(intent_result, context)
    
    def handle_unknown_intent(self, user_message: str, session_id: str) -> FallbackResponse:
        """Xử lý intent không xác định"""
        
        # Kiểm tra escalation
        if self._should_escalate(user_message):
            return self._create_escalation_response()
        
        # Phân tích context để đưa ra gợi ý phù hợp
        context = context_manager.get_conversation_context(session_id, last_n=5)
        recent_intents = [turn.get('intent') for turn in context if turn.get('intent')]
        
        # Gợi ý dựa trên context
        if 'product_search' in recent_intents:
            suggestions = self.suggestion_templates['product_suggestions'][:4]
            message = "Mình có thể giúp bạn tìm sản phẩm theo các cách sau:"
        elif 'price_inquiry' in recent_intents:
            suggestions = ["Hỏi giá sản phẩm cụ thể", "Tìm theo tầm giá", "Xem khuyến mãi"]
            message = "Bạn có thể hỏi về giá cả theo các cách này:"
        else:
            suggestions = self.suggestion_templates['general_suggestions'][:6]
            message = "Mình có thể hỗ trợ bạn những việc sau:"
        
        return FallbackResponse(
            message=message,
            suggestions=suggestions,
            clarification_needed=True,
            escalate_to_human=False,
            confidence_boost_tips=self._get_confidence_boost_tips()
        )
    
    def _handle_unclear_product_search(self, intent_result: IntentResult, 
                                     context: List[Dict]) -> FallbackResponse:
        """Xử lý tìm kiếm sản phẩm không rõ ràng"""
        
        # Kiểm tra entities có sẵn
        entities = intent_result.entities
        missing_info = []
        
        if not entities.get('product_type'):
            missing_info.append("loại sản phẩm")
        if not entities.get('size'):
            missing_info.append("size")
        if not entities.get('price_range'):
            missing_info.append("tầm giá")
        
        if missing_info:
            clarification = random.choice(self.clarification_templates['product_search_unclear'])
            suggestions = self.suggestion_templates['product_suggestions'][:4]
        else:
            clarification = "Mình đã hiểu yêu cầu của bạn. Để tìm chính xác hơn, bạn có thể bổ sung thêm thông tin:"
            suggestions = ["Chọn màu sắc", "Chọn thương hiệu", "Xem tất cả kết quả"]
        
        return FallbackResponse(
            message=clarification,
            suggestions=suggestions,
            clarification_needed=True,
            escalate_to_human=False,
            confidence_boost_tips=["Mô tả chi tiết sản phẩm", "Đưa ra ví dụ cụ thể"]
        )
    
    def _handle_unclear_price_inquiry(self, intent_result: IntentResult, 
                                    context: List[Dict]) -> FallbackResponse:
        """Xử lý hỏi giá không rõ ràng"""
        
        clarification = random.choice(self.clarification_templates['price_unclear'])
        suggestions = [
            "Hỏi giá sản phẩm cụ thể",
            "Tìm theo tầm giá",
            "Xem sản phẩm giảm giá",
            "So sánh giá"
        ]
        
        return FallbackResponse(
            message=clarification,
            suggestions=suggestions,
            clarification_needed=True,
            escalate_to_human=False,
            confidence_boost_tips=["Nêu tên sản phẩm cụ thể", "Đưa ra tầm giá mong muốn"]
        )
    
    def _handle_unclear_size_inquiry(self, intent_result: IntentResult, 
                                   context: List[Dict]) -> FallbackResponse:
        """Xử lý hỏi size không rõ ràng"""
        
        clarification = random.choice(self.clarification_templates['size_unclear'])
        suggestions = [
            "Tư vấn size theo chiều cao/cân nặng",
            "Xem bảng size chi tiết",
            "So sánh size các hãng",
            "Hỏi size sản phẩm cụ thể"
        ]
        
        return FallbackResponse(
            message=clarification,
            suggestions=suggestions,
            clarification_needed=True,
            escalate_to_human=False,
            confidence_boost_tips=["Cung cấp thông tin cơ thể", "Nêu sản phẩm cụ thể"]
        )
    
    def _handle_general_unclear(self, intent_result: IntentResult, 
                              context: List[Dict]) -> FallbackResponse:
        """Xử lý trường hợp chung không rõ ràng"""
        
        clarification = random.choice(self.clarification_templates['general_unclear'])
        suggestions = self.suggestion_templates['general_suggestions'][:5]
        
        return FallbackResponse(
            message=clarification,
            suggestions=suggestions,
            clarification_needed=True,
            escalate_to_human=False,
            confidence_boost_tips=["Sử dụng từ khóa đơn giản", "Chia nhỏ câu hỏi"]
        )
    
    def _should_escalate(self, user_message: str) -> bool:
        """Kiểm tra có cần chuyển lên human không"""
        message_lower = user_message.lower()
        return any(trigger in message_lower for trigger in self.escalation_triggers)
    
    def _create_escalation_response(self) -> FallbackResponse:
        """Tạo response cho escalation"""
        return FallbackResponse(
            message="Mình hiểu bạn cần hỗ trợ chuyên sâu hơn. Để được tư vấn tốt nhất, mình sẽ kết nối bạn với tư vấn viên của shop.",
            suggestions=[
                "Kết nối tư vấn viên",
                "Gửi phản hồi",
                "Liên hệ hotline",
                "Chat với manager"
            ],
            clarification_needed=False,
            escalate_to_human=True,
            confidence_boost_tips=[]
        )
    
    def _get_confidence_boost_tips(self) -> List[str]:
        """Lấy tips để cải thiện giao tiếp"""
        tips = [
            "Sử dụng từ khóa đơn giản và rõ ràng",
            "Chia nhỏ câu hỏi thành nhiều phần",
            "Đưa ra ví dụ cụ thể",
            "Mô tả chi tiết nhu cầu",
            "Sử dụng các từ khóa phổ biến"
        ]
        return random.sample(tips, 2)
    
    def generate_contextual_suggestions(self, session_id: str) -> List[str]:
        """Tạo gợi ý dựa trên context"""
        context = context_manager.get_conversation_context(session_id, last_n=3)
        
        if not context:
            return self.suggestion_templates['general_suggestions'][:4]
        
        # Phân tích intent gần đây
        recent_intents = [turn.get('intent') for turn in context]
        
        if 'product_search' in recent_intents:
            return [
                "Lọc theo giá",
                "Chọn size khác", 
                "Xem sản phẩm tương tự",
                "So sánh sản phẩm"
            ]
        elif 'price_inquiry' in recent_intents:
            return [
                "Xem khuyến mãi",
                "So sánh giá",
                "Tìm sản phẩm rẻ hơn",
                "Hỏi về combo"
            ]
        else:
            return self.suggestion_templates['general_suggestions'][:4]

# Global instance
fallback_handler = FallbackHandler()

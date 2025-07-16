"""
Enhanced AI Service with Advanced Conversation Handling
Integrates intent detection, context management, and fallback handling
"""

import uuid
import time
import logging
from typing import Dict, List, Any, Optional
from django.conf import settings
from django.contrib.auth.models import User

from .intent_detector import intent_detector, IntentType
from .context_manager import context_manager
from .fallback_handler import fallback_handler
from .smart_ai_service import SmartAIProcessor

logger = logging.getLogger(__name__)

class EnhancedAIService_DISABLED:
    """Enhanced AI Service với conversation handling nâng cao"""
    
    def __init__(self):
        self.smart_processor = SmartAIProcessor()
        self.ai_providers = self._initialize_ai_providers()
        
    def _initialize_ai_providers(self):
        """Initialize AI providers với fallback chain"""
        providers = {}
        
        # Gemini AI (primary)
        try:
            from .gemini_service import gemini_service
            if gemini_service.is_available():
                providers['gemini'] = gemini_service
                logger.info("Gemini AI initialized successfully")
        except Exception as e:
            logger.warning(f"Gemini AI not available: {e}")
        
        # Ollama AI (secondary)
        try:
            from .ollama_service import ollama_service
            if ollama_service.is_available():
                providers['ollama'] = ollama_service
                logger.info("Ollama AI initialized successfully")
        except Exception as e:
            logger.warning(f"Ollama AI not available: {e}")
        
        return providers
    
    def generate_response(self, message: str, user=None, context: Dict = None) -> Dict:
        """Generate intelligent response với advanced conversation handling"""
        try:
            start_time = time.time()
            
            # Get or create session
            session_id = context.get('session_id') if context else str(uuid.uuid4())
            user_id = user.id if user and user.is_authenticated else None
            
            session = context_manager.get_session(session_id)
            if not session:
                session = context_manager.create_session(session_id, user_id)
            
            # Detect intent với advanced processing
            intent_result = intent_detector.detect_intent(message, context)
            
            # Handle low confidence hoặc unknown intents
            if intent_result.confidence < 0.7 or intent_result.intent == IntentType.UNKNOWN:
                return self._handle_uncertain_intent(intent_result, message, session_id, start_time)
            
            # Route to appropriate handler based on intent
            response = self._route_intent(intent_result, message, user, session_id)
            
            # Add conversation turn to context
            context_manager.add_conversation_turn(
                session_id, message, response['message'], 
                intent_result.intent.value, intent_result.entities
            )
            
            # Update user preferences if applicable
            if user_id:
                context_manager.update_user_preferences_from_interaction(
                    session_id, intent_result.entities
                )
            
            # Enhance response với session info
            response.update({
                'session_id': session_id,
                'intent': intent_result.intent.value,
                'confidence': intent_result.confidence,
                'response_time': time.time() - start_time,
                'entities': intent_result.entities
            })
            
            return response
                
        except Exception as e:
            logger.error(f"Error in generate_response: {e}")
            return self._create_error_response(e, context)
    
    def _handle_uncertain_intent(self, intent_result, message: str, session_id: str, start_time: float) -> Dict:
        """Xử lý intent không chắc chắn"""
        if intent_result.intent == IntentType.UNKNOWN:
            fallback_response = fallback_handler.handle_unknown_intent(message, session_id)
        else:
            fallback_response = fallback_handler.handle_low_confidence_intent(
                intent_result, message, session_id
            )
        
        if fallback_response.escalate_to_human:
            return self._handle_human_escalation(fallback_response, session_id, start_time)
        else:
            return self._create_fallback_response(fallback_response, session_id, start_time)
    
    def _route_intent(self, intent_result, message: str, user, session_id: str) -> Dict:
        """Route intent to appropriate handler"""
        intent = intent_result.intent
        
        if intent == IntentType.PRODUCT_SEARCH:
            return self._handle_product_search(message, user, intent_result.entities)
        elif intent == IntentType.PRICE_INQUIRY:
            return self._handle_price_inquiry(message, user, intent_result.entities)
        elif intent == IntentType.STOCK_CHECK:
            return self._handle_stock_check(message, user, intent_result.entities)
        elif intent == IntentType.SIZE_INQUIRY:
            return self._handle_size_inquiry(message, user, intent_result.entities)
        elif intent == IntentType.POLICY_QUESTION:
            return self._handle_policy_question(message, user, intent_result.entities)
        elif intent == IntentType.RECOMMENDATION:
            return self._handle_recommendation(message, user, session_id)
        elif intent == IntentType.GREETING:
            return self._handle_greeting(message, user, session_id)
        elif intent == IntentType.GOODBYE:
            return self._handle_goodbye(message, user, session_id)
        elif intent == IntentType.COMPLAINT:
            return self._handle_complaint(message, user, session_id)
        elif intent == IntentType.ORDER_STATUS:
            return self._handle_order_status(message, user, intent_result.entities)
        else:
            return self._handle_general_chat(message, user, session_id)
    
    def _handle_product_search(self, message: str, user, entities: Dict) -> Dict:
        """Xử lý tìm kiếm sản phẩm"""
        # Sử dụng smart processor để tìm sản phẩm
        result = self.smart_processor._handle_product_search(message, message.lower())
        
        if result.get('suggested_products'):
            products = result['suggested_products'][:5]  # Top 5 products
            
            # Format response
            if products:
                product_list = []
                for i, product in enumerate(products, 1):
                    product_list.append(
                        f"{i}. **{product['name']}**\n"
                        f"   💰 {product['price']:,.0f} VND\n"
                        f"   🏷️ {product['brand']} - {product['category']}\n"
                        f"   👉 [Xem chi tiết](/#/products/{product['id']})"
                    )
                
                message = f"🛍️ **Tìm thấy {len(products)} sản phẩm phù hợp:**\n\n" + "\n\n".join(product_list)
                
                quick_replies = ['Xem tất cả', 'Lọc theo giá', 'Tìm khác']
                if len(products) >= 5:
                    quick_replies.insert(0, 'Xem thêm')
            else:
                message = "Xin lỗi, không tìm thấy sản phẩm nào phù hợp. Bạn có thể thử:\n\n• Mô tả chi tiết hơn\n• Tìm theo thương hiệu\n• Xem tất cả sản phẩm"
                quick_replies = ['Xem tất cả sản phẩm', 'Thương hiệu phổ biến', 'Hỗ trợ']
            
            return {
                'message': message,
                'suggested_products': products,
                'quick_replies': quick_replies,
                'metadata': {
                    'intent': 'product_search',
                    'results_count': len(products)
                }
            }
        
        return result
    
    def _handle_price_inquiry(self, message: str, user, entities: Dict) -> Dict:
        """Xử lý hỏi giá"""
        # Extract product info from entities
        if entities.get('product_type'):
            product_type = entities['product_type'][0]
            # Search for products of this type
            products = self.smart_processor.db_reader.search_products(product_type)[:3]
            
            if products:
                price_info = []
                for product in products:
                    price_info.append(f"• **{product['name']}**: {product['price']:,.0f} VND")
                
                message = f"💰 **Giá {product_type}:**\n\n" + "\n".join(price_info)
                quick_replies = ['Xem chi tiết', 'So sánh giá', 'Tìm rẻ hơn']
            else:
                message = f"Xin lỗi, không tìm thấy thông tin giá cho {product_type}. Bạn có thể tìm sản phẩm cụ thể hơn không?"
                quick_replies = ['Tìm sản phẩm', 'Xem tất cả', 'Hỗ trợ']
        else:
            message = "Bạn muốn hỏi giá sản phẩm nào? Vui lòng cho mình biết tên hoặc loại sản phẩm cụ thể."
            quick_replies = ['Áo thun', 'Quần jean', 'Giày thể thao', 'Xem tất cả']
        
        return {
            'message': message,
            'quick_replies': quick_replies,
            'metadata': {'intent': 'price_inquiry'}
        }
    
    def _handle_greeting(self, message: str, user, session_id: str) -> Dict:
        """Xử lý lời chào"""
        user_name = user.get_full_name() if user and user.is_authenticated else "bạn"
        
        greetings = [
            f"Xin chào {user_name}! 👋 Chào mừng đến với shop thời trang của chúng tôi!",
            f"Hi {user_name}! 😊 Mình có thể giúp gì cho bạn hôm nay?",
            f"Chào {user_name}! ✨ Rất vui được hỗ trợ bạn!"
        ]
        
        import random
        message = random.choice(greetings)
        
        quick_replies = [
            '🛍️ Tìm sản phẩm',
            '🔥 Sản phẩm hot',
            '💰 Khuyến mãi',
            '📏 Tư vấn size',
            '❓ Hỗ trợ'
        ]
        
        return {
            'message': message,
            'quick_replies': quick_replies,
            'metadata': {'intent': 'greeting'}
        }
    
    def _handle_stock_check(self, message: str, user, entities: Dict) -> Dict:
        """Xử lý kiểm tra tồn kho"""
        if entities.get('product_type'):
            product_type = entities['product_type'][0]
            products = self.smart_processor.db_reader.search_products(product_type)

            if products:
                in_stock = [p for p in products if p.get('stock', 0) > 0]
                out_of_stock = [p for p in products if p.get('stock', 0) == 0]

                message = f"📦 **Tình trạng tồn kho {product_type}:**\n\n"

                if in_stock:
                    message += f"✅ **Còn hàng ({len(in_stock)} sản phẩm):**\n"
                    for product in in_stock[:3]:
                        message += f"• {product['name']} - Còn {product.get('stock', 'N/A')} sản phẩm\n"

                if out_of_stock:
                    message += f"\n❌ **Hết hàng ({len(out_of_stock)} sản phẩm):**\n"
                    for product in out_of_stock[:2]:
                        message += f"• {product['name']}\n"

                quick_replies = ['Đặt hàng', 'Thông báo khi có hàng', 'Tìm sản phẩm khác']
            else:
                message = f"Không tìm thấy thông tin tồn kho cho {product_type}."
                quick_replies = ['Tìm sản phẩm khác', 'Liên hệ hỗ trợ']
        else:
            message = "Bạn muốn kiểm tra tồn kho sản phẩm nào?"
            quick_replies = ['Áo thun', 'Quần jean', 'Giày', 'Tất cả sản phẩm']

        return {
            'message': message,
            'quick_replies': quick_replies,
            'metadata': {'intent': 'stock_check'}
        }

    def _handle_size_inquiry(self, message: str, user, entities: Dict) -> Dict:
        """Xử lý tư vấn size"""
        size_guide = {
            'áo': {
                'S': 'Cao 1m50-1m60, Nặng 45-55kg',
                'M': 'Cao 1m60-1m70, Nặng 55-65kg',
                'L': 'Cao 1m70-1m80, Nặng 65-75kg',
                'XL': 'Cao 1m80+, Nặng 75kg+'
            },
            'quần': {
                '28': 'Eo 70-72cm',
                '29': 'Eo 72-75cm',
                '30': 'Eo 75-78cm',
                '31': 'Eo 78-81cm',
                '32': 'Eo 81-84cm'
            }
        }

        if entities.get('product_type'):
            product_type = entities['product_type'][0]
            if 'áo' in product_type:
                guide = size_guide['áo']
                message = f"📏 **Bảng size {product_type}:**\n\n"
                for size, desc in guide.items():
                    message += f"• **Size {size}**: {desc}\n"
            elif 'quần' in product_type:
                guide = size_guide['quần']
                message = f"📏 **Bảng size {product_type}:**\n\n"
                for size, desc in guide.items():
                    message += f"• **Size {size}**: {desc}\n"
            else:
                message = f"Bảng size cho {product_type} đang được cập nhật. Bạn có thể liên hệ để được tư vấn chi tiết."
        else:
            message = "📏 **Tư vấn size:**\n\nBạn cần tư vấn size cho loại sản phẩm nào? Hoặc có thể cung cấp chiều cao, cân nặng để mình tư vấn chính xác hơn."

        quick_replies = ['Tư vấn size áo', 'Tư vấn size quần', 'Đo size', 'Liên hệ tư vấn']

        return {
            'message': message,
            'quick_replies': quick_replies,
            'metadata': {'intent': 'size_inquiry'}
        }

    def _handle_policy_question(self, message: str, user, entities: Dict) -> Dict:
        """Xử lý câu hỏi về chính sách"""
        policies = {
            'đổi trả': {
                'title': '🔄 Chính sách đổi trả',
                'content': '• Đổi trả trong 7 ngày\n• Sản phẩm còn nguyên tem, chưa qua sử dụng\n• Miễn phí đổi size trong 3 ngày đầu'
            },
            'vận chuyển': {
                'title': '🚚 Thông tin vận chuyển',
                'content': '• Giao hàng toàn quốc\n• Phí ship: 30k (miễn phí đơn >500k)\n• Thời gian: 2-3 ngày nội thành, 3-5 ngày ngoại thành'
            },
            'thanh toán': {
                'title': '💳 Phương thức thanh toán',
                'content': '• COD (thanh toán khi nhận hàng)\n• Chuyển khoản ngân hàng\n• Ví điện tử (Momo, ZaloPay)\n• Thẻ tín dụng/ghi nợ'
            },
            'bảo hành': {
                'title': '🛡️ Chính sách bảo hành',
                'content': '• Bảo hành lỗi sản xuất 30 ngày\n• Hỗ trợ sửa chữa với chi phí hợp lý\n• Đổi mới nếu lỗi nghiêm trọng'
            }
        }

        message_lower = message.lower()

        if any(word in message_lower for word in ['đổi', 'trả', 'hoàn']):
            policy = policies['đổi trả']
        elif any(word in message_lower for word in ['ship', 'giao', 'vận chuyển']):
            policy = policies['vận chuyển']
        elif any(word in message_lower for word in ['thanh toán', 'payment', 'cod']):
            policy = policies['thanh toán']
        elif any(word in message_lower for word in ['bảo hành', 'warranty', 'lỗi']):
            policy = policies['bảo hành']
        else:
            # General policy overview
            message = "📋 **Chính sách của shop:**\n\nBạn muốn xem thông tin về chính sách nào?"
            quick_replies = ['Đổi trả', 'Vận chuyển', 'Thanh toán', 'Bảo hành']
            return {
                'message': message,
                'quick_replies': quick_replies,
                'metadata': {'intent': 'policy_question'}
            }

        message = f"{policy['title']}\n\n{policy['content']}"
        quick_replies = ['Chính sách khác', 'Liên hệ hỗ trợ', 'Đặt hàng']

        return {
            'message': message,
            'quick_replies': quick_replies,
            'metadata': {'intent': 'policy_question'}
        }

    def _handle_recommendation(self, message: str, user, session_id: str) -> Dict:
        """Xử lý gợi ý sản phẩm"""
        # Get user preferences from context
        session = context_manager.get_session(session_id)
        user_prefs = session.user_preferences if session else None

        # Get trending products
        trending_products = self.smart_processor.db_reader.get_trending_products()[:4]

        if user_prefs and user_prefs.preferred_categories:
            # Personalized recommendations
            category = user_prefs.preferred_categories[0]
            products = self.smart_processor.db_reader.search_products(category)[:3]
            message = f"✨ **Gợi ý dành riêng cho bạn ({category}):**\n\n"
        else:
            # General recommendations
            products = trending_products
            message = "🔥 **Sản phẩm hot nhất hiện tại:**\n\n"

        if products:
            for i, product in enumerate(products, 1):
                message += f"{i}. **{product['name']}**\n   💰 {product['price']:,.0f} VND\n\n"

        quick_replies = ['Xem chi tiết', 'Gợi ý khác', 'Tìm theo sở thích', 'Tất cả sản phẩm']

        return {
            'message': message,
            'suggested_products': products,
            'quick_replies': quick_replies,
            'metadata': {'intent': 'recommendation'}
        }

    def _handle_goodbye(self, message: str, user, session_id: str) -> Dict:
        """Xử lý lời tạm biệt"""
        farewells = [
            "Cảm ơn bạn đã ghé thăm shop! 👋 Hẹn gặp lại bạn sớm nhé!",
            "Tạm biệt và cảm ơn bạn! 😊 Chúc bạn có những trải nghiệm mua sắm tuyệt vời!",
            "Bye bye! 🌟 Nhớ quay lại khi cần hỗ trợ nhé!"
        ]

        import random
        message = random.choice(farewells)

        quick_replies = ['Mua sắm tiếp', 'Theo dõi đơn hàng', 'Liên hệ sau']

        return {
            'message': message,
            'quick_replies': quick_replies,
            'metadata': {'intent': 'goodbye'}
        }

    def _handle_complaint(self, message: str, user, session_id: str) -> Dict:
        """Xử lý khiếu nại"""
        message = """😔 **Rất xin lỗi vì trải nghiệm không tốt của bạn!**

Chúng tôi rất coi trọng phản hồi của khách hàng. Để hỗ trợ bạn tốt nhất:

1. 📞 **Hotline**: 1900-xxxx (8h-22h)
2. 💬 **Chat trực tiếp** với manager
3. 📧 **Email**: support@shop.com
4. 📝 **Form khiếu nại** chi tiết

Chúng tôi cam kết giải quyết trong 24h!"""

        quick_replies = ['Chat với manager', 'Gọi hotline', 'Gửi email', 'Form khiếu nại']

        return {
            'message': message,
            'quick_replies': quick_replies,
            'metadata': {
                'intent': 'complaint',
                'priority': 'high',
                'escalate': True
            }
        }

    def _handle_order_status(self, message: str, user, entities: Dict) -> Dict:
        """Xử lý trạng thái đơn hàng"""
        if user and user.is_authenticated:
            # In real implementation, query order database
            message = f"""📦 **Trạng thái đơn hàng của {user.get_full_name() or user.username}:**

🔍 Để kiểm tra chính xác, bạn vui lòng cung cấp:
• Mã đơn hàng
• Số điện thoại đặt hàng
• Email đặt hàng

Hoặc đăng nhập tài khoản để xem tất cả đơn hàng."""

            quick_replies = ['Nhập mã đơn', 'Xem tất cả đơn', 'Liên hệ hỗ trợ']
        else:
            message = """📦 **Tra cứu đơn hàng:**

Để kiểm tra trạng thái đơn hàng, bạn cần:
• Đăng nhập tài khoản
• Hoặc cung cấp mã đơn hàng + SĐT

Chúng tôi sẽ cập nhật thông tin chi tiết cho bạn!"""

            quick_replies = ['Đăng nhập', 'Nhập mã đơn', 'Liên hệ hỗ trợ']

        return {
            'message': message,
            'quick_replies': quick_replies,
            'metadata': {'intent': 'order_status'}
        }

    def _handle_general_chat(self, message: str, user, session_id: str) -> Dict:
        """Xử lý chat chung với AI"""
        # Try AI providers in order of preference
        for provider_name, provider in self.ai_providers.items():
            try:
                ai_response = provider.generate_response(message)
                if ai_response.get('success'):
                    return {
                        'message': ai_response['message'],
                        'quick_replies': ['Tìm sản phẩm', 'Xem thống kê', 'Gợi ý khác', 'Hỗ trợ'],
                        'metadata': {
                            'intent': 'general_ai',
                            'ai_provider': provider_name,
                            'model_used': ai_response.get('model_used'),
                            'response_time': ai_response.get('response_time')
                        }
                    }
            except Exception as e:
                logger.warning(f"AI provider {provider_name} failed: {e}")
                continue
        
        # Fallback to rule-based response
        return {
            'message': 'Cảm ơn bạn đã nhắn tin! Tôi là chatbot hỗ trợ mua sắm. Tôi có thể giúp bạn tìm sản phẩm, check giá, tư vấn size và nhiều thứ khác. Bạn cần hỗ trợ gì?',
            'quick_replies': ['Tìm sản phẩm', 'Hỏi giá', 'Tư vấn size', 'Chính sách shop'],
            'metadata': {'intent': 'general_fallback'}
        }
    
    def _create_fallback_response(self, fallback_response, session_id: str, start_time: float) -> Dict:
        """Tạo response từ fallback handler"""
        return {
            'message': fallback_response.message,
            'quick_replies': fallback_response.suggestions,
            'session_id': session_id,
            'response_time': time.time() - start_time,
            'metadata': {
                'intent': 'fallback',
                'clarification_needed': fallback_response.clarification_needed,
                'confidence_tips': fallback_response.confidence_boost_tips
            }
        }
    
    def _handle_human_escalation(self, fallback_response, session_id: str, start_time: float) -> Dict:
        """Xử lý chuyển lên human support"""
        return {
            'message': fallback_response.message,
            'quick_replies': fallback_response.suggestions,
            'session_id': session_id,
            'response_time': time.time() - start_time,
            'metadata': {
                'intent': 'human_escalation',
                'escalate': True,
                'priority': 'high'
            }
        }
    
    def _create_error_response(self, error: Exception, context: Dict = None) -> Dict:
        """Tạo error response"""
        return {
            'message': 'Xin lỗi, có lỗi xảy ra. Vui lòng thử lại sau.',
            'quick_replies': ['Thử lại', 'Hỗ trợ'],
            'session_id': context.get('session_id') if context else str(uuid.uuid4()),
            'metadata': {'error': str(error), 'intent': 'error'}
        }

# Global instance - DISABLED
# enhanced_ai_service = EnhancedAIService_DISABLED()

# Temporary fallback to force import error
class _DisabledService:
    def __getattr__(self, name):
        raise ImportError("Enhanced AI service is disabled")

enhanced_ai_service = _DisabledService()

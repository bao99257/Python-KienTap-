"""
Hybrid Chatbot Service - Combines reliable core logic with AI enhancement
"""

import logging
from typing import Dict, List, Optional
from .size_consultant import size_consultant

logger = logging.getLogger(__name__)


class HybridChatbot:
    """Hybrid chatbot với core logic ổn định + AI enhancement"""
    
    def __init__(self):
        self.size_consultant = size_consultant
    
    def process_message(self, message: str, user=None, session_id=None) -> Dict:
        """Xử lý message với hybrid approach"""
        try:
            # 1. Detect intent
            intent = self._detect_intent(message)
            
            # 2. Route to appropriate handler
            if intent == 'size_consultation':
                return self._handle_size_consultation(message)
            elif intent == 'size_guide':
                return self._handle_size_guide(message)
            elif intent == 'policy':
                return self._handle_policy(message)
            elif intent == 'product_search':
                return self._handle_product_search(message)
            elif intent == 'greeting':
                return self._handle_greeting(message)
            elif intent == 'emotional':
                return self._handle_emotional(message)
            else:
                return self._handle_general_chat(message)
                
        except Exception as e:
            logger.error(f"Error in hybrid chatbot: {e}")
            return self._generate_error_response()
    
    def _detect_intent(self, message: str) -> str:
        """Detect intent với priority logic"""
        message_lower = message.lower()
        
        # Size consultation (highest priority)
        # Check if message contains measurements
        has_measurements = any(pattern in message_lower for pattern in ['1m', 'cao', 'nặng', 'kg', 'cm'])
        has_size_keywords = any(word in message_lower for word in ['size', 'cỡ', 'mặc', 'áo', 'quần', 'đầm', 'váy'])

        if has_measurements and has_size_keywords:
            return 'size_consultation'

        # Also detect if just measurements are provided (implicit size consultation)
        if has_measurements and any(pattern in message_lower for pattern in ['1m', 'cao.*nặng', 'nặng.*cao']):
            return 'size_consultation'
        
        # Size guide requests
        if any(phrase in message_lower for phrase in ['bảng size', 'size chart', 'hướng dẫn size', 'tư vấn size']):
            return 'size_guide'

        # Policy questions
        if any(phrase in message_lower for phrase in ['chính sách', 'policy', 'quy định', 'đổi trả', 'bảo hành']):
            return 'policy'
        
        # Product search
        if any(word in message_lower for word in ['tìm', 'search', 'mua', 'có']) and \
           any(word in message_lower for word in ['áo', 'quần', 'giày', 'sản phẩm']):
            return 'product_search'
        
        # Greetings
        if any(word in message_lower for word in ['chào', 'hello', 'hi', 'xin chào']):
            return 'greeting'
        
        # Emotional expressions
        if any(word in message_lower for word in ['buồn', 'vui', 'hạnh phúc', 'tức giận', 'stress']):
            return 'emotional'
        
        return 'general_chat'
    
    def _handle_size_consultation(self, message: str) -> Dict:
        """Xử lý tư vấn size với measurements cụ thể"""
        # Extract measurements
        measurements = self.size_consultant.extract_measurements(message)
        
        if not measurements.get('height') or not measurements.get('weight'):
            return {
                'message': """📏 **Để tư vấn size chính xác, mình cần thông tin:**

🔸 **Chiều cao** (ví dụ: 1m56 hoặc 156cm)
🔸 **Cân nặng** (ví dụ: 59kg)
🔸 **Loại sản phẩm** (áo, quần, đầm, giày)

**Ví dụ:** "Tôi cao 1m65, nặng 56kg, muốn mua áo thun" """,
                'quick_replies': ['📏 Bảng size chi tiết', '👕 Size áo', '👖 Size quần', '👗 Size đầm'],
                'intent': 'size_consultation_guide'
            }
        
        # Detect product type
        product_type = self.size_consultant.detect_product_type(message)
        
        # Get size recommendation
        result = self.size_consultant.recommend_size(measurements, product_type)
        
        if not result['success']:
            # Check if it's a special case (outside normal range)
            if result.get('special_case'):
                return {
                    'message': f"⚠️ **Trường hợp đặc biệt:**\n\n{result['message']}\n\n💡 **Gợi ý:**\n• Liên hệ trực tiếp để được đo size cá nhân\n• Có thể cần may đo riêng\n• Shop sẽ tư vấn size phù hợp nhất",
                    'quick_replies': ['📞 Liên hệ ngay', '📏 Bảng size tham khảo', '💬 Chat với tư vấn viên', '🔄 Nhập lại thông tin'],
                    'intent': 'size_consultation_special_case'
                }
            else:
                return {
                    'message': f"❌ {result['message']}",
                    'quick_replies': ['📏 Bảng size chi tiết', '📞 Liên hệ tư vấn', '🔄 Thử lại'],
                    'intent': 'size_consultation_failed'
                }
        
        # Format successful response
        height = measurements['height']
        weight = measurements['weight']
        recommended_sizes = result['recommended_sizes']
        
        message_text = f"""✅ **Tư vấn size cho bạn:**

👤 **Thông tin:** Cao {height}cm, nặng {weight}kg
📦 **Sản phẩm:** {self._get_product_name(product_type)}

🎯 **Size gợi ý:**"""
        
        for size_info in recommended_sizes:
            size = size_info['size']
            fit = size_info['fit']
            note = size_info.get('note', '')
            
            if fit == 'perfect':
                message_text += f"\n• **Size {size}** ✨ (Vừa vặn)"
            else:
                message_text += f"\n• **Size {size}** (Có thể phù hợp)"
            
            if note:
                message_text += f" - {note}"
        
        # Add specific advice and notes
        if result.get('note'):
            message_text += f"\n\n💡 **Lưu ý:** {result['note']}"

        if product_type == 'ao':
            message_text += "\n\n💡 **Thêm:** Áo hoodie/oversize có thể tăng 1 size nếu thích form rộng"
        elif product_type == 'giay':
            if result.get('note') and 'note' not in message_text:
                message_text += f"\n\n💡 **Lưu ý:** {result['note']}"
        
        return {
            'message': message_text,
            'quick_replies': ['📏 Bảng size chi tiết', '🛍️ Xem sản phẩm', '🔄 Tư vấn khác', '📞 Hỗ trợ'],
            'intent': 'size_consultation_success',
            'metadata': {
                'measurements': measurements,
                'recommended_sizes': recommended_sizes,
                'product_type': product_type
            }
        }
    
    def _handle_size_guide(self, message: str) -> Dict:
        """Hiển thị bảng size chi tiết"""
        return {
            'message': """📏 **BẢNG SIZE CHI TIẾT**

👕 **ÁO NAM/NỮ/HOODIE:**
• **XS:** Nam 155-160cm/45-50kg, Nữ 150-155cm/40-45kg
• **S:** Nam 160-165cm/50-58kg, Nữ 155-160cm/45-50kg
• **M:** Nam 165-170cm/58-65kg, Nữ 160-165cm/50-58kg
• **L:** Nam 170-175cm/65-73kg, Nữ 165-170cm/58-65kg
• **XL:** Nam 175-180cm/73-80kg, Nữ 165-175cm/65-75kg

👖 **QUẦN NAM/NỮ:**
• **XS:** Eo 65-70cm, 45-50kg (Size 26-27)
• **S:** Eo 70-75cm, 50-58kg (Size 28)
• **M:** Eo 75-80cm, 58-65kg (Size 29-30)
• **L:** Eo 80-85cm, 65-73kg (Size 31-32)
• **XL:** Eo 85-90cm, 73-80kg (Size 33-34)

👗 **ĐẦM/VÁY:**
• **XS:** Ngực 78-82cm, Eo 60-65cm, 40-45kg
• **S:** Ngực 83-86cm, Eo 66-69cm, 45-50kg
• **M:** Ngực 87-90cm, Eo 70-74cm, 50-58kg
• **L:** Ngực 91-95cm, Eo 75-79cm, 58-65kg

👟 **GIÀY:** Size 36-45, đo chiều dài chân chính xác

📋 **CHÍNH SÁCH TỪ VẤN SIZE:**
Trước khi đặt hàng, bạn có thể tham khảo bảng size trên để chọn size phù hợp. Nếu không chắc chắn về size hoặc muốn được tư vấn cá nhân, vui lòng liên hệ trực tiếp với shop để được hỗ trợ tốt nhất.""",
            'quick_replies': ['📏 Tư vấn size cá nhân', '👕 Size áo', '👖 Size quần', '👗 Size đầm'],
            'intent': 'size_guide'
        }
    
    def _handle_policy(self, message: str) -> Dict:
        """Xử lý câu hỏi về chính sách"""
        return {
            'message': """📋 **CHÍNH SÁCH TƯ VẤN SIZE THỜI TRANG**

🔸 **Trước khi đặt hàng:**
Chúng tôi cung cấp bảng tham khảo size dựa trên chiều cao và cân nặng. Bạn có thể tham khảo bảng size để chọn size phù hợp.

🔸 **Nếu không chắc chắn về size:**
• Liên hệ trực tiếp với shop để được tư vấn cá nhân
• Cung cấp số đo 3 vòng để tư vấn chính xác hơn
• Tham khảo review từ khách hàng có cùng thể hình

🔸 **Cam kết của shop:**
• Tư vấn size miễn phí trước khi mua
• Hỗ trợ đổi size nếu không vừa (theo điều kiện)
• Bảng size được cập nhật thường xuyên

📞 **Liên hệ tư vấn:** [Thông tin liên hệ]""",
            'quick_replies': ['📏 Xem bảng size', '📞 Liên hệ tư vấn', '🔄 Đổi trả', '❓ Hỗ trợ khác'],
            'intent': 'policy'
        }

    def _handle_product_search(self, message: str) -> Dict:
        """Xử lý tìm kiếm sản phẩm (placeholder)"""
        return {
            'message': '🛍️ **Tìm kiếm sản phẩm:**\n\nChức năng tìm kiếm đang được phát triển. Hiện tại bạn có thể:\n• Tư vấn size\n• Xem bảng size\n• Liên hệ hỗ trợ',
            'quick_replies': ['📏 Tư vấn size', '🛍️ Xem sản phẩm', '📞 Liên hệ', '❓ Hỗ trợ'],
            'intent': 'product_search'
        }
    
    def _handle_greeting(self, message: str) -> Dict:
        """Xử lý chào hỏi"""
        return {
            'message': """👋 **Xin chào! Chào mừng bạn đến với shop thời trang!**

Mình có thể giúp bạn:
🔸 **Tư vấn size** dựa trên chiều cao/cân nặng
🔸 **Xem bảng size** chi tiết cho từng loại sản phẩm  
🔸 **Tìm sản phẩm** phù hợp
🔸 **Trả lời** mọi câu hỏi về shop

Bạn cần hỗ trợ gì nhé? 😊""",
            'quick_replies': ['📏 Tư vấn size', '🛍️ Tìm sản phẩm', '📋 Bảng size', '❓ Hỗ trợ'],
            'intent': 'greeting'
        }
    
    def _handle_emotional(self, message: str) -> Dict:
        """Xử lý cảm xúc"""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['buồn', 'sad', 'tệ']):
            return {
                'message': '😢 **Ôi không! Tại sao bạn lại buồn vậy?**\n\nCó phải vì không tìm được sản phẩm ưng ý không? Để mình giúp bạn tìm những món đồ đẹp để tâm trạng tốt hơn nhé! ✨',
                'quick_replies': ['🛍️ Tìm sản phẩm', '📏 Tư vấn size', '💝 Sản phẩm hot', '😊 Động viên'],
                'intent': 'emotional_support'
            }
        else:
            return {
                'message': '😊 **Thật tuyệt khi bạn vui vẻ!**\n\nHãy để mình chia sẻ niềm vui này bằng cách giúp bạn tìm những sản phẩm thời trang đẹp nhé! ✨',
                'quick_replies': ['🛍️ Mua sắm vui', '📏 Tư vấn size', '💝 Sản phẩm hot', '🎉 Khuyến mãi'],
                'intent': 'positive_emotion'
            }
    
    def _handle_general_chat(self, message: str) -> Dict:
        """Xử lý chat chung với fallback content đầy đủ"""

        # Detect specific topics for better responses
        message_lower = message.lower()

        if any(word in message_lower for word in ['shop', 'cửa hàng', 'địa chỉ']):
            return {
                'message': """🏪 **Thông tin về shop:**

Chúng tôi là shop thời trang chuyên cung cấp:
• Áo thun, áo hoodie, áo sơ mi
• Quần jean, jogger, quần tây
• Đầm, váy thời trang
• Giày dép các loại

📍 **Dịch vụ:** Tư vấn size miễn phí, giao hàng toàn quốc
📞 **Liên hệ:** [Thông tin liên hệ sẽ được cập nhật]""",
                'quick_replies': ['📏 Tư vấn size', '🛍️ Xem sản phẩm', '📋 Chính sách', '📞 Liên hệ'],
                'intent': 'shop_info'
            }

        return {
            'message': """💬 **Xin lỗi, mình chưa hiểu rõ câu hỏi của bạn.**

Nhưng mình có thể giúp bạn:
🔸 **Tư vấn size** dựa trên chiều cao/cân nặng
🔸 **Xem bảng size** chi tiết và chính sách
🔸 **Tìm sản phẩm** phù hợp với nhu cầu
🔸 **Trả lời** các câu hỏi về shop và sản phẩm

Hãy cho mình biết bạn cần hỗ trợ gì nhé! 😊""",
            'quick_replies': ['📏 Tư vấn size', '🛍️ Tìm sản phẩm', '📋 Bảng size', '❓ Hỗ trợ'],
            'intent': 'general_chat'
        }
    
    def _get_product_name(self, product_type: str) -> str:
        """Chuyển đổi product type thành tên hiển thị"""
        names = {
            'ao': 'Áo (Nam/Nữ/Hoodie)',
            'quan': 'Quần (Jean/Jogger/Tây)',
            'dam_vay': 'Đầm/Váy',
            'giay': 'Giày/Dép'
        }
        return names.get(product_type, 'Sản phẩm')
    
    def _generate_error_response(self) -> Dict:
        """Tạo response khi có lỗi"""
        return {
            'message': '❌ **Xin lỗi, có lỗi xảy ra.**\n\nVui lòng thử lại hoặc liên hệ hỗ trợ.',
            'quick_replies': ['🔄 Thử lại', '📞 Liên hệ hỗ trợ', '📏 Tư vấn size', '🏠 Trang chủ'],
            'intent': 'error'
        }


# Global instance
hybrid_chatbot = HybridChatbot()

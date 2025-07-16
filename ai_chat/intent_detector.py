"""
Advanced Intent Detection System for E-commerce Chatbot
Supports Vietnamese language with slang, abbreviations, and chat language
"""

import re
import logging
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class IntentType(Enum):
    """Định nghĩa các loại intent chính"""
    PRODUCT_SEARCH = "product_search"
    PRICE_INQUIRY = "price_inquiry" 
    STOCK_CHECK = "stock_check"
    SIZE_INQUIRY = "size_inquiry"
    POLICY_QUESTION = "policy_question"
    RECOMMENDATION = "recommendation"
    GREETING = "greeting"
    GOODBYE = "goodbye"
    COMPLAINT = "complaint"
    ORDER_STATUS = "order_status"
    GENERAL_CHAT = "general_chat"
    UNKNOWN = "unknown"

@dataclass
class IntentResult:
    """Kết quả phân tích intent"""
    intent: IntentType
    confidence: float
    entities: Dict[str, any]
    keywords: List[str]
    context_needed: bool = False

class VietnameseIntentDetector:
    """Hệ thống nhận diện intent tiếng Việt với xử lý ngôn ngữ chat"""
    
    def __init__(self):
        self.intent_patterns = self._build_intent_patterns()
        self.entity_extractors = self._build_entity_extractors()
        self.slang_normalizer = self._build_slang_normalizer()
        
    def _build_slang_normalizer(self) -> Dict[str, str]:
        """Chuẩn hóa ngôn ngữ chat, viết tắt tiếng Việt"""
        return {
            # Viết tắt thông dụng
            'k': 'không', 'ko': 'không', 'khong': 'không',
            'dc': 'được', 'đc': 'được', 'duoc': 'được',
            'vs': 'với', 'voi': 'với', 'w/': 'với',
            'tui': 'tôi', 'mik': 'tôi', 'mk': 'tôi',
            'bn': 'bạn', 'b': 'bạn', 'bro': 'bạn',
            'r': 'rồi', 'roi': 'rồi', 'oy': 'rồi',
            'ntn': 'như thế nào', 'sao': 'như thế nào',
            'bao h': 'bao giờ', 'khi nao': 'khi nào',
            'bh': 'bây giờ', 'h': 'giờ', 'bay h': 'bây giờ',
            'tks': 'cảm ơn', 'thanks': 'cảm ơn', 'ty': 'cảm ơn',
            'ok': 'được', 'oke': 'được', 'okie': 'được',
            'sr': 'sorry', 'sry': 'xin lỗi',
            
            # Từ lóng về sản phẩm
            'đồ': 'sản phẩm', 'món': 'sản phẩm', 'thứ': 'sản phẩm',
            'cái': 'sản phẩm', 'em': 'sản phẩm',
            'xinh': 'đẹp', 'cute': 'đẹp', 'dễ thương': 'đẹp',
            'chất': 'tốt', 'ngon': 'tốt', 'xịn': 'tốt',
            'rẻ': 'giá thấp', 'bèo': 'giá thấp', 'hời': 'giá thấp',
            'đắt': 'giá cao', 'chát': 'giá cao', 'mắc': 'giá cao',
            
            # Số tiền teen code
            '100k': '100000', '200k': '200000', '500k': '500000',
            '1tr': '1000000', '2tr': '2000000', '5tr': '5000000',
            'củ': '000000', 'triệu': '000000',
        }
    
    def _build_intent_patterns(self) -> Dict[IntentType, List[str]]:
        """Xây dựng patterns cho từng intent"""
        return {
            IntentType.PRODUCT_SEARCH: [
                r'(tìm|tìm kiếm|có|bán|shop|cần|muốn|xem).*(áo|quần|giày|dép|váy|đầm|sản phẩm)',
                r'(show|hiện|xem).*(sản phẩm|đồ|món)',
                r'(áo|quần|giày|dép|váy|đầm).*(nào|gì|nào|loại)',
                r'(có|bán).*(gì|những gì|sản phẩm nào)',
            ],
            
            IntentType.PRICE_INQUIRY: [
                r'(giá|bao nhiêu|giá tiền|giá cả|chi phí|phí)',
                r'(bao nhiêu|giá).*(tiền|đồng|k|nghìn|triệu)',
                r'(rẻ|đắt|mắc|chát|bèo|hời).*(không|ko|k)',
                r'(trong|dưới|trên|từ).*(100k|200k|500k|1tr|triệu)',
            ],
            
            IntentType.STOCK_CHECK: [
                r'(còn|có|tồn|sẵn).*(hàng|không|ko|k)',
                r'(hết|sold out|out of stock)',
                r'(còn|có).*(size|màu|loại)',
                r'(check|kiểm tra).*(tồn kho|hàng)',
            ],
            
            IntentType.SIZE_INQUIRY: [
                r'(size|kích thước|cỡ|số)',
                r'(S|M|L|XL|XXL|28|29|30|31|32)',
                r'(vừa|lớn|nhỏ|rộng|chật)',
                r'(cao|nặng).*(bao nhiêu|mét|kg|cm)',
            ],
            
            IntentType.POLICY_QUESTION: [
                r'(đổi|trả|hoàn|bảo hành|chính sách)',
                r'(ship|giao hàng|vận chuyển|phí ship)',
                r'(thanh toán|payment|cod|chuyển khoản)',
                r'(bảo hành|warranty|lỗi|hỏng)',
            ],
            
            IntentType.RECOMMENDATION: [
                r'(gợi ý|tư vấn|recommend|suggest)',
                r'(nên|should|phù hợp|hợp)',
                r'(outfit|phối đồ|mix|match)',
                r'(trend|hot|mới|popular|nổi)',
            ],
            
            IntentType.GREETING: [
                r'^(hi|hello|chào|xin chào|hey)',
                r'(có ai|có người|có không)',
                r'(shop|cửa hàng).*(mở|đóng|hoạt động)',
            ],
            
            IntentType.GOODBYE: [
                r'(bye|tạm biệt|chào|cảm ơn|thanks|ty)',
                r'(hẹn gặp lại|see you|tks)',
                r'(đủ rồi|thôi|ok|oke)',
            ],
            
            IntentType.COMPLAINT: [
                r'(tệ|dở|kém|không tốt|chất lượng kém)',
                r'(khiếu nại|complain|phàn nàn)',
                r'(lỗi|hỏng|sai|không đúng)',
                r'(thất vọng|disappointed|không hài lòng)',
            ],
            
            IntentType.ORDER_STATUS: [
                r'(đơn hàng|order|mua|đặt)',
                r'(trạng thái|status|tình trạng)',
                r'(giao|ship|nhận|về)',
                r'(mã đơn|order id|tracking)',
            ]
        }
    
    def _build_entity_extractors(self) -> Dict[str, List[str]]:
        """Trích xuất entities từ text"""
        return {
            'product_type': [
                r'(áo thun|áo sơ mi|áo khoác|áo len)',
                r'(quần jean|quần kaki|quần short|quần dài)',
                r'(giày thể thao|giày cao gót|dép|sandal)',
                r'(váy|đầm|chân váy)',
            ],
            'size': [
                r'\b(S|M|L|XL|XXL|XXXL)\b',
                r'\b(28|29|30|31|32|33|34|35|36|37|38|39|40|41|42)\b',
                r'(size|cỡ)\s*(\w+)',
            ],
            'color': [
                r'(đen|trắng|xám|nâu|be|kem)',
                r'(đỏ|xanh|vàng|tím|hồng|cam)',
                r'(navy|black|white|blue|red|green)',
            ],
            'price_range': [
                r'(dưới|under|below)\s*(\d+k?|\d+\s*triệu)',
                r'(từ|from)\s*(\d+k?)\s*(đến|to)\s*(\d+k?)',
                r'(\d+k|\d+\s*triệu|\d+\s*nghìn)',
            ],
            'brand': [
                r'(nike|adidas|gucci|zara|h&m|uniqlo)',
                r'(local brand|việt nam|domestic)',
            ]
        }
    
    def normalize_text(self, text: str) -> str:
        """Chuẩn hóa text với slang và viết tắt"""
        text = text.lower().strip()
        
        # Thay thế slang và viết tắt
        for slang, normal in self.slang_normalizer.items():
            text = re.sub(r'\b' + re.escape(slang) + r'\b', normal, text)
        
        # Chuẩn hóa khoảng trắng
        text = re.sub(r'\s+', ' ', text)
        
        return text
    
    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Trích xuất entities từ text"""
        entities = {}
        
        for entity_type, patterns in self.entity_extractors.items():
            matches = []
            for pattern in patterns:
                found = re.findall(pattern, text, re.IGNORECASE)
                if found:
                    matches.extend([match if isinstance(match, str) else match[0] for match in found])
            
            if matches:
                entities[entity_type] = list(set(matches))  # Remove duplicates
        
        return entities
    
    def detect_intent(self, text: str, context: Dict = None) -> IntentResult:
        """Phân tích intent chính từ text"""
        # Chuẩn hóa text
        normalized_text = self.normalize_text(text)
        
        # Trích xuất entities
        entities = self.extract_entities(normalized_text)
        
        # Tính điểm cho từng intent
        intent_scores = {}
        matched_keywords = []
        
        for intent_type, patterns in self.intent_patterns.items():
            score = 0
            keywords = []
            
            for pattern in patterns:
                matches = re.findall(pattern, normalized_text, re.IGNORECASE)
                if matches:
                    score += len(matches) * 10  # Base score
                    keywords.extend([m if isinstance(m, str) else ' '.join(m) for m in matches])
            
            # Bonus điểm nếu có entities liên quan
            if intent_type == IntentType.PRODUCT_SEARCH and 'product_type' in entities:
                score += 15
            elif intent_type == IntentType.PRICE_INQUIRY and 'price_range' in entities:
                score += 15
            elif intent_type == IntentType.SIZE_INQUIRY and 'size' in entities:
                score += 15
            
            if score > 0:
                intent_scores[intent_type] = score
                matched_keywords.extend(keywords)
        
        # Xác định intent có điểm cao nhất
        if intent_scores:
            best_intent = max(intent_scores.items(), key=lambda x: x[1])
            confidence = min(best_intent[1] / 100.0, 1.0)  # Normalize to 0-1
            
            return IntentResult(
                intent=best_intent[0],
                confidence=confidence,
                entities=entities,
                keywords=list(set(matched_keywords)),
                context_needed=confidence < 0.7
            )
        
        # Fallback to general chat or unknown
        if len(normalized_text.split()) <= 3:
            return IntentResult(
                intent=IntentType.GENERAL_CHAT,
                confidence=0.5,
                entities=entities,
                keywords=[],
                context_needed=True
            )
        
        return IntentResult(
            intent=IntentType.UNKNOWN,
            confidence=0.3,
            entities=entities,
            keywords=[],
            context_needed=True
        )

# Global instance
intent_detector = VietnameseIntentDetector()

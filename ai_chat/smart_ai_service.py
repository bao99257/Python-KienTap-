"""
Smart AI Service - Enhanced with advanced conversation handling, intent detection, and context management
"""

import re
import json
import uuid
import time
from typing import Dict, List, Any, Optional
from django.db.models import Q, Count, Avg, Sum, Max, Min
from django.utils import timezone
from django.contrib.auth.models import User
from django.conf import settings
import logging

from .intent_detector import intent_detector, IntentType
from .context_manager import context_manager
from .fallback_handler import fallback_handler

logger = logging.getLogger(__name__)


class DatabaseReader:
    """Đọc và phân tích toàn bộ database"""
    
    @staticmethod
    def get_all_products():
        """Lấy tất cả sản phẩm"""
        try:
            from api.models import Product
            products = Product.objects.select_related('brand', 'category').all()
            return [
                {
                    'id': p.id,
                    'name': p.name,
                    'description': p.description,
                    'price': float(p.price),
                    'brand': p.brand.title if p.brand else 'Unknown',
                    'category': p.category.title if p.category else 'Unknown',
                    'image': p.image.url if p.image else None
                }
                for p in products
            ]
        except Exception as e:
            logger.error(f"Error getting products: {e}")
            return []

    @staticmethod
    def get_trending_products(limit=5):
        """Lấy sản phẩm hot/trending"""
        try:
            from api.models import Product
            # Get products ordered by some criteria (e.g., newest, most popular)
            # For now, just get random products as trending
            products = Product.objects.select_related('brand', 'category').order_by('-id')[:limit]
            return [
                {
                    'id': p.id,
                    'name': p.name,
                    'description': p.description,
                    'price': float(p.price),
                    'brand': p.brand.title if p.brand else 'Unknown',
                    'category': p.category.title if p.category else 'Unknown',
                    'image': p.image.url if p.image else None,
                    'link': f'/product/{p.id}/'
                }
                for p in products
            ]
        except Exception as e:
            logger.error(f"Error getting trending products: {e}")
            return []
    
    @staticmethod
    def get_all_brands():
        """Lấy tất cả thương hiệu"""
        try:
            from api.models import Brand
            brands = Brand.objects.annotate(product_count=Count('product')).all()
            return [
                {
                    'id': b.id,
                    'title': b.title,
                    'product_count': b.product_count
                }
                for b in brands
            ]
        except Exception as e:
            logger.error(f"Error getting brands: {e}")
            return []
    
    @staticmethod
    def get_all_categories():
        """Lấy tất cả danh mục"""
        try:
            from api.models import Category
            categories = Category.objects.annotate(product_count=Count('product')).all()
            return [
                {
                    'id': c.id,
                    'title': c.title,
                    'product_count': c.product_count
                }
                for c in categories
            ]
        except Exception as e:
            logger.error(f"Error getting categories: {e}")
            return []
    
    @staticmethod
    def get_database_stats():
        """Lấy thống kê tổng quan"""
        try:
            from api.models import Product, Brand, Category
            
            # Product stats
            product_stats = Product.objects.aggregate(
                total=Count('id'),
                avg_price=Avg('price'),
                min_price=Min('price'),
                max_price=Max('price')
            )
            
            # Top brands
            top_brands = Brand.objects.annotate(
                product_count=Count('product')
            ).order_by('-product_count')[:5]
            
            # Top categories
            top_categories = Category.objects.annotate(
                product_count=Count('product')
            ).order_by('-product_count')[:5]
            
            return {
                'products': {
                    'total': product_stats['total'] or 0,
                    'avg_price': product_stats['avg_price'] or 0,
                    'min_price': product_stats['min_price'] or 0,
                    'max_price': product_stats['max_price'] or 0
                },
                'brands': {
                    'total': Brand.objects.count(),
                    'top': [{'title': b.title, 'products': b.product_count} for b in top_brands]
                },
                'categories': {
                    'total': Category.objects.count(),
                    'top': [{'name': c.title, 'products': c.product_count} for c in top_categories]
                }
            }
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {}
    
    @staticmethod
    def search_products(query: str, filters: Dict = None):
        """Tìm kiếm sản phẩm thông minh"""
        try:
            from api.models import Product
            from django.db.models import Q

            # Base query
            products = Product.objects.select_related('brand', 'category')

            # Text search với từ khóa riêng lẻ
            if query:
                # Tách từ khóa và loại bỏ stop words
                stop_words = ['tìm', 'có', 'bán', 'shop', 'màu', 'size', 'cỡ', 'giá', 'vnd', 'đồng', 'không', 'gì']
                important_keywords = ['áo', 'quần', 'giày', 'dép']  # Từ khóa sản phẩm quan trọng

                keywords = []
                for word in query.lower().split():
                    word = word.strip()
                    # Giữ lại từ khóa quan trọng hoặc từ dài hơn 2 ký tự (không phải stop word)
                    if word in important_keywords or (len(word) > 2 and word not in stop_words):
                        keywords.append(word)

                if keywords:
                    search_q = Q()
                    for keyword in keywords:
                        search_q |= (
                            Q(name__icontains=keyword) |
                            Q(description__icontains=keyword) |
                            Q(brand__title__icontains=keyword) |
                            Q(category__title__icontains=keyword)
                        )
                    products = products.filter(search_q)
                else:
                    # Nếu không có keyword hợp lệ, tìm theo category chung
                    query_lower = query.lower()
                    if any(word in query_lower for word in ['áo', 'shirt', 'top']):
                        products = products.filter(Q(category__title__icontains='áo'))
                    elif any(word in query_lower for word in ['quần', 'pants', 'jean']):
                        products = products.filter(Q(category__title__icontains='quần'))
                    elif any(word in query_lower for word in ['giày', 'shoes', 'sneaker']):
                        products = products.filter(Q(category__title__icontains='giày'))
            
            # Apply filters
            if filters:
                if filters.get('brand'):
                    products = products.filter(brand__title__icontains=filters['brand'])
                if filters.get('category'):
                    products = products.filter(category__title__icontains=filters['category'])
                if filters.get('min_price'):
                    products = products.filter(price__gte=filters['min_price'])
                if filters.get('max_price'):
                    products = products.filter(price__lte=filters['max_price'])
                if filters.get('color'):
                    products = products.filter(variants__color__name__icontains=filters['color'])
                if filters.get('size'):
                    products = products.filter(variants__size__name__icontains=filters['size'])

            # Serialize results
            results = []
            for p in products[:20]:  # Limit to 20 results
                results.append({
                    'id': p.id,
                    'name': p.name,
                    'description': p.description,
                    'price': float(p.price),
                    'brand': p.brand.title if p.brand else 'Unknown',
                    'category': p.category.title if p.category else 'Unknown',
                    'image': p.image.url if p.image else None
                })
            
            return results
        except Exception as e:
            logger.error(f"Error searching products: {e}")
            return []


class SmartAIProcessor:
    """AI processor thông minh"""
    
    def __init__(self):
        self.db_reader = DatabaseReader()
    
    def process_message(self, message: str, user=None, session_id=None) -> Dict:
        """Xử lý tin nhắn thông minh với intent detection và context memory"""
        try:
            # Initialize context management
            if not session_id:
                import uuid
                session_id = str(uuid.uuid4())

            # Get or create session context
            try:
                from .context_manager import context_manager
                session = context_manager.get_session(session_id)
                if not session:
                    user_id = user.id if user and hasattr(user, 'id') else None
                    session = context_manager.create_session(session_id, user_id)

                # Get conversation context for better responses
                conversation_context = context_manager.get_conversation_context(session_id, last_n=3)
                context_available = True
            except ImportError:
                conversation_context = []
                context_available = False
            # Use advanced intent detection
            try:
                from .intent_detector import intent_detector, IntentType
                intent_result = intent_detector.detect_intent(message)
                detected_intent = intent_result.intent.value
                confidence = intent_result.confidence
                entities = intent_result.entities
            except ImportError:
                # Fallback to simple detection
                detected_intent = self._simple_intent_detection(message.lower())
                confidence = 0.8
                entities = {}

            # Debug log
            logger.info(f"Message: '{message}' -> Intent: '{detected_intent}'")

            # Route based on detected intent - prioritize Gemini AI for most queries

            # Handle quick reply actions first
            if self._is_quick_reply_action(message):
                response = self._handle_quick_reply_action(message, user)
            elif detected_intent == 'database_query' or self._is_database_query(message.lower()):
                response = self._handle_database_query(message.lower())
            elif detected_intent == 'product_search' or self._is_product_search(message.lower()):
                response = self._handle_product_search(message, message.lower())
            elif self._is_stats_request(message.lower()):
                response = self._handle_stats_request(message.lower())
            else:
                # Let Hybrid AI handle most conversations including:
                # - greetings, goodbyes
                # - price inquiries
                # - size consultations (IMPORTANT: including height/weight questions)
                # - policy questions
                # - stock checks
                # - recommendations
                # - general chat
                response = self._handle_general_chat(message, user, detected_intent)

            # Add intent metadata to response
            if isinstance(response, dict):
                # Don't override intent if already set by handler
                if 'intent' not in response:
                    response['intent'] = detected_intent
                response['confidence'] = confidence
                response['entities'] = entities
                response['session_id'] = session_id

                # Add context info
                if context_available:
                    response['context'] = {
                        'conversation_turns': len(conversation_context),
                        'session_duration': 'active'
                    }

            # Save conversation turn to context
            if context_available and isinstance(response, dict):
                try:
                    context_manager.add_conversation_turn(
                        session_id,
                        message,
                        response.get('message', ''),
                        detected_intent,
                        entities
                    )

                    # Update user preferences if applicable
                    if user and hasattr(user, 'id') and entities:
                        context_manager.update_user_preferences_from_interaction(session_id, entities)

                except Exception as e:
                    logger.warning(f"Failed to save conversation context: {e}")

            return response

        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return self._generate_error_response()

    def _simple_intent_detection(self, message: str) -> str:
        """Simple fallback intent detection với priority"""

        # Database queries (highest priority)
        if self._is_database_query(message):
            return 'database_query'

        # General questions (high priority) - should go to Gemini AI
        general_patterns = [
            'ngày', 'tháng', 'năm', 'thời tiết', 'hôm nay', 'ngày mai',
            'thế nào', 'như thế nào', 'tại sao', 'vì sao', 'khi nào'
        ]
        if any(pattern in message for pattern in general_patterns):
            # But exclude product-related questions
            if not any(word in message for word in ['áo', 'quần', 'giày', 'sản phẩm', 'shop', 'mua']):
                return 'general_chat'

        # Greeting patterns - specific greetings only
        if any(phrase in message for phrase in ['xin chào', 'hello', 'hi', 'chào bạn', 'chào shop']):
            return 'greeting'

        # Goodbye patterns
        elif any(word in message for word in ['tạm biệt', 'bye', 'cảm ơn', 'goodbye']):
            return 'goodbye'

        # Price inquiry patterns (higher priority) - more specific
        elif any(phrase in message for phrase in ['giá', 'bao nhiêu tiền', 'giá cả', 'chi phí']):
            return 'price_inquiry'
        elif 'bao nhiêu' in message and any(word in message for word in ['áo', 'quần', 'giày', 'sản phẩm', 'đồ']):
            return 'price_inquiry'

        # Size inquiry patterns (high priority when has height/weight info)
        elif any(phrase in message for phrase in ['tư vấn size', 'size', 'cỡ', 'kích thước', 'tư vấn cỡ']):
            return 'size_inquiry'
        elif any(pattern in message for pattern in ['1m', 'cao', 'nặng', 'kg']) and any(word in message for word in ['mặc', 'size', 'cỡ']):
            return 'size_inquiry'

        # Policy question patterns
        elif any(phrase in message for phrase in ['chính sách', 'đổi trả', 'bảo hành', 'vận chuyển', 'ship']):
            return 'policy_question'

        # Stock check patterns
        elif any(phrase in message for phrase in ['còn hàng', 'tồn kho', 'stock', 'có hàng', 'hết hàng']):
            return 'stock_check'

        # Recommendation patterns
        elif any(phrase in message for phrase in ['gợi ý', 'recommend', 'tư vấn outfit', 'outfit', 'phối đồ']):
            return 'recommendation'

        # Product search patterns (lower priority) - more specific
        elif any(phrase in message for phrase in ['tìm áo', 'tìm quần', 'tìm giày', 'tìm sản phẩm', 'search']):
            return 'product_search'
        elif any(word in message for word in ['áo', 'quần', 'giày']) and any(word in message for word in ['tìm', 'mua', 'cần', 'muốn']):
            return 'product_search'

        else:
            return 'general_chat'

    def _handle_price_inquiry(self, message: str, entities: Dict) -> Dict:
        """Xử lý hỏi giá sản phẩm"""
        # Extract product type from entities or message
        product_type = None
        if entities.get('product_type'):
            product_type = entities['product_type'][0]
        else:
            # Simple extraction
            for product in ['áo thun', 'áo sơ mi', 'quần jean', 'giày']:
                if product in message.lower():
                    product_type = product
                    break

        if product_type:
            products = self.db_reader.search_products(product_type)[:3]
            if products:
                message_text = f"💰 **Giá {product_type}:**\n\n"
                for i, product in enumerate(products, 1):
                    message_text += f"{i}. **{product['name']}**: {product['price']:,.0f} VND\n"

                return {
                    'message': message_text,
                    'suggested_products': products,
                    'quick_replies': ['Xem chi tiết', 'So sánh giá', 'Tìm rẻ hơn'],
                    'intent': 'price_inquiry'
                }

        return {
            'message': 'Bạn muốn hỏi giá sản phẩm nào? Vui lòng cho mình biết tên hoặc loại sản phẩm cụ thể.',
            'quick_replies': ['Áo thun', 'Quần jean', 'Giày thể thao', 'Xem tất cả'],
            'intent': 'price_inquiry'
        }

    def _handle_size_inquiry(self, message: str, entities: Dict) -> Dict:
        """Xử lý tư vấn size"""
        size_guide = {
            'áo': {
                'S': 'Cao 1m50-1m60, Nặng 45-55kg',
                'M': 'Cao 1m60-1m70, Nặng 55-65kg',
                'L': 'Cao 1m70-1m80, Nặng 65-75kg',
                'XL': 'Cao 1m80+, Nặng 75kg+'
            }
        }

        # Check if asking about specific product
        if 'áo' in message.lower():
            guide = size_guide['áo']
            message_text = "📏 **Bảng size áo:**\n\n"
            for size, desc in guide.items():
                message_text += f"• **Size {size}**: {desc}\n"

            return {
                'message': message_text,
                'quick_replies': ['Tư vấn size cụ thể', 'Đo size', 'Liên hệ tư vấn'],
                'intent': 'size_inquiry'
            }

        return {
            'message': '📏 **Tư vấn size:**\n\nBạn cần tư vấn size cho loại sản phẩm nào? Hoặc có thể cung cấp chiều cao, cân nặng để mình tư vấn chính xác hơn.',
            'quick_replies': ['Tư vấn size áo', 'Tư vấn size quần', 'Đo size'],
            'intent': 'size_inquiry'
        }

    def _handle_policy_question(self, message: str) -> Dict:
        """Xử lý câu hỏi về chính sách"""
        message_lower = message.lower()

        if any(word in message_lower for word in ['đổi', 'trả', 'hoàn']):
            policy_text = """🔄 **Chính sách đổi trả:**

• Đổi trả trong 7 ngày kể từ ngày nhận hàng
• Sản phẩm còn nguyên tem mác, chưa qua sử dụng
• Miễn phí đổi size trong 3 ngày đầu
• Chi phí vận chuyển đổi trả theo quy định

Liên hệ hotline để được hỗ trợ chi tiết!"""

        elif any(word in message_lower for word in ['ship', 'giao', 'vận chuyển']):
            policy_text = """🚚 **Thông tin vận chuyển:**

• Giao hàng toàn quốc
• Phí ship: 30k (miễn phí đơn >500k)
• Thời gian: 2-3 ngày nội thành, 3-5 ngày ngoại thành
• Đóng gói cẩn thận, bảo đảm chất lượng"""

        else:
            policy_text = """📋 **Chính sách shop:**

🔄 Đổi trả trong 7 ngày
🚚 Giao hàng toàn quốc
💳 Nhiều hình thức thanh toán
🛡️ Bảo hành sản phẩm

Bạn muốn xem chi tiết chính sách nào?"""

        return {
            'message': policy_text,
            'quick_replies': ['Đổi trả', 'Vận chuyển', 'Thanh toán', 'Bảo hành'],
            'intent': 'policy_question'
        }

    def _handle_stock_check(self, message: str, entities: Dict) -> Dict:
        """Xử lý kiểm tra tồn kho"""
        # Extract product from message
        product_type = None
        for product in ['áo thun', 'áo sơ mi', 'quần jean', 'giày']:
            if product in message.lower():
                product_type = product
                break

        if product_type:
            products = self.db_reader.search_products(product_type)
            if products:
                in_stock = [p for p in products if p.get('stock', 0) > 0]

                message_text = f"📦 **Tình trạng tồn kho {product_type}:**\n\n"

                if in_stock:
                    message_text += f"✅ **Còn hàng ({len(in_stock)} sản phẩm)**\n"
                    for product in in_stock[:3]:
                        stock_info = f"Còn {product.get('stock', 'N/A')}" if product.get('stock') else "Có sẵn"
                        message_text += f"• {product['name']} - {stock_info}\n"
                else:
                    message_text += "❌ **Tạm hết hàng**\n"
                    message_text += "Sản phẩm đang được nhập thêm, vui lòng theo dõi!"

                return {
                    'message': message_text,
                    'suggested_products': in_stock[:3] if in_stock else products[:3],
                    'quick_replies': ['Đặt hàng', 'Thông báo khi có hàng', 'Tìm sản phẩm khác'],
                    'intent': 'stock_check'
                }

        return {
            'message': 'Bạn muốn kiểm tra tồn kho sản phẩm nào?',
            'quick_replies': ['Áo thun', 'Quần jean', 'Giày', 'Tất cả sản phẩm'],
            'intent': 'stock_check'
        }

    def _handle_greeting(self, message: str, user) -> Dict:
        """Xử lý lời chào"""
        user_name = user.get_full_name() if user and hasattr(user, 'get_full_name') else "bạn"

        greetings = [
            f"Xin chào {user_name}! 👋 Chào mừng đến với shop thời trang!",
            f"Hi {user_name}! 😊 Mình có thể giúp gì cho bạn hôm nay?",
            f"Chào {user_name}! ✨ Rất vui được hỗ trợ bạn!"
        ]

        import random
        message_text = random.choice(greetings)

        return {
            'message': message_text,
            'quick_replies': ['🛍️ Tìm sản phẩm', '🔥 Sản phẩm hot', '💰 Khuyến mãi', '📏 Tư vấn size'],
            'intent': 'greeting'
        }

    def _handle_goodbye(self, message: str, user) -> Dict:
        """Xử lý lời tạm biệt"""
        farewells = [
            "Cảm ơn bạn đã ghé thăm shop! 👋 Hẹn gặp lại bạn sớm nhé!",
            "Tạm biệt và cảm ơn bạn! 😊 Chúc bạn có những trải nghiệm mua sắm tuyệt vời!",
            "Bye bye! 🌟 Nhớ quay lại khi cần hỗ trợ nhé!"
        ]

        import random
        message_text = random.choice(farewells)

        return {
            'message': message_text,
            'quick_replies': ['Mua sắm tiếp', 'Theo dõi đơn hàng', 'Liên hệ sau'],
            'intent': 'goodbye'
        }
    
    def _is_database_query(self, message: str) -> bool:
        """Kiểm tra có phải query database không"""
        keywords = [
            'có bao nhiêu', 'tổng cộng', 'số lượng', 'danh sách', 'liệt kê',
            'cho tôi biết', 'hiển thị', 'tất cả', 'toàn bộ'
        ]
        return any(keyword in message for keyword in keywords)
    
    def _is_product_search(self, message: str) -> bool:
        """Kiểm tra có phải tìm sản phẩm không"""
        # Từ khóa tìm kiếm trực tiếp
        search_keywords = ['tìm', 'search', 'mua', 'cần', 'muốn']

        # Từ khóa sản phẩm
        product_keywords = ['áo', 'quần', 'giày', 'dép', 'sản phẩm']

        # Từ khóa hỏi về sản phẩm
        inquiry_keywords = ['có', 'bán', 'shop']

        # Từ khóa size (để nhận diện "size 42" là product search)
        size_keywords = ['size', 'cỡ', 'kích thước']

        # Kiểm tra các pattern
        has_search = any(keyword in message for keyword in search_keywords)
        has_product = any(keyword in message for keyword in product_keywords)
        has_inquiry = any(keyword in message for keyword in inquiry_keywords)
        has_size = any(keyword in message for keyword in size_keywords)

        # IMPORTANT: Exclude size consultation questions (height/weight info)
        if any(pattern in message for pattern in ['1m', 'cao', 'nặng', 'kg']) and has_size:
            return False  # This is size consultation, not product search

        # Nếu có từ khóa tìm kiếm hoặc (có từ khóa hỏi + từ khóa sản phẩm) hoặc có sản phẩm
        return has_search or (has_inquiry and has_product) or has_product
    
    def _is_stats_request(self, message: str) -> bool:
        """Kiểm tra có phải yêu cầu thống kê không"""
        keywords = [
            'thống kê', 'báo cáo', 'doanh thu', 'bán chạy', 'top', 'phổ biến',
            'nhiều nhất', 'ít nhất', 'trung bình'
        ]
        return any(keyword in message for keyword in keywords)
    
    def _is_recommendation_request(self, message: str) -> bool:
        """Kiểm tra có phải yêu cầu gợi ý không"""
        keywords = [
            'gợi ý', 'recommend', 'tư vấn', 'nên mua', 'phù hợp', 'đề xuất'
        ]
        return any(keyword in message for keyword in keywords)
    
    def _handle_database_query(self, message: str) -> Dict:
        """Xử lý query database"""
        try:
            response_text = ""
            
            if 'sản phẩm' in message:
                products = self.db_reader.get_all_products()
                response_text = f"📊 **Database có tổng cộng {len(products)} sản phẩm:**\n\n"
                
                # Group by category
                categories = {}
                for product in products:
                    cat = product['category']
                    if cat not in categories:
                        categories[cat] = []
                    categories[cat].append(product)
                
                for cat, prods in categories.items():
                    response_text += f"**{cat}**: {len(prods)} sản phẩm\n"
                
                response_text += f"\n💰 **Giá trung bình**: {sum(p['price'] for p in products) / len(products):,.0f} VND"
            
            elif 'thương hiệu' in message or 'brand' in message:
                brands = self.db_reader.get_all_brands()
                response_text = f"🏷️ **Database có {len(brands)} thương hiệu:**\n\n"
                
                for brand in brands[:10]:  # Top 10
                    response_text += f"• **{brand['title']}**: {brand['product_count']} sản phẩm\n"
            
            elif 'danh mục' in message or 'category' in message:
                categories = self.db_reader.get_all_categories()
                response_text = f"📂 **Database có {len(categories)} danh mục:**\n\n"
                
                for cat in categories:
                    response_text += f"• **{cat['title']}**: {cat['product_count']} sản phẩm\n"
            
            else:
                stats = self.db_reader.get_database_stats()
                response_text = f"📊 **Tổng quan Database:**\n\n"
                response_text += f"🛍️ **Sản phẩm**: {stats['products']['total']}\n"
                response_text += f"🏷️ **Thương hiệu**: {stats['brands']['total']}\n"
                response_text += f"📂 **Danh mục**: {stats['categories']['total']}\n"
                response_text += f"💰 **Giá trung bình**: {stats['products']['avg_price']:,.0f} VND\n"
                response_text += f"💸 **Giá thấp nhất**: {stats['products']['min_price']:,.0f} VND\n"
                response_text += f"💎 **Giá cao nhất**: {stats['products']['max_price']:,.0f} VND"
            
            return {
                'message': response_text,
                'quick_replies': ['Xem sản phẩm', 'Thống kê chi tiết', 'Tìm sản phẩm'],
                'metadata': {'intent': 'database_query', 'type': 'success'}
            }
            
        except Exception as e:
            logger.error(f"Error handling database query: {e}")
            return self._generate_error_response()
    
    def _parse_search_filters(self, message: str) -> Dict:
        """Parse advanced search filters from message"""
        filters = {}
        message_lower = message.lower()

        # Parse price filters
        price_patterns = [
            (r'dưới (\d+)k', 'max_price'),
            (r'under (\d+)k', 'max_price'),
            (r'trên (\d+)k', 'min_price'),
            (r'over (\d+)k', 'min_price'),
            (r'từ (\d+)k đến (\d+)k', 'price_range'),
            (r'(\d+)k - (\d+)k', 'price_range'),
            (r'(\d+)k đến (\d+)k', 'price_range')
        ]

        for pattern, filter_type in price_patterns:
            match = re.search(pattern, message_lower)
            if match:
                if filter_type == 'max_price':
                    filters['max_price'] = int(match.group(1)) * 1000
                elif filter_type == 'min_price':
                    filters['min_price'] = int(match.group(1)) * 1000
                elif filter_type == 'price_range':
                    if len(match.groups()) == 2:
                        filters['min_price'] = int(match.group(1)) * 1000
                        filters['max_price'] = int(match.group(2)) * 1000
                break

        # Parse size filters
        size_pattern = r'\b(S|M|L|XL|XXL|28|29|30|31|32|33|34|35|36|37|38|39|40|41|42)\b'
        size_matches = re.findall(size_pattern, message_lower, re.IGNORECASE)
        if size_matches:
            filters['sizes'] = list(set(size_matches))

        # Parse gender filters
        if 'nam' in message_lower:
            filters['gender'] = 'nam'
        elif 'nữ' in message_lower:
            filters['gender'] = 'nữ'

        return filters

    def _handle_product_search(self, original_message: str, message: str) -> Dict:
        """Xử lý tìm kiếm sản phẩm với advanced filters"""
        try:
            # Parse advanced filters
            advanced_filters = self._parse_search_filters(original_message)

            # Extract basic filters (legacy)
            basic_filters = self._extract_filters(message)
            
            # Merge filters
            merged_filters = {**basic_filters, **advanced_filters}

            # Search products with advanced filters
            products = self.db_reader.search_products(original_message, merged_filters)

            # Apply additional filtering if needed
            if advanced_filters.get('max_price'):
                products = [p for p in products if p['price'] <= advanced_filters['max_price']]

            if advanced_filters.get('min_price'):
                products = [p for p in products if p['price'] >= advanced_filters['min_price']]

            if advanced_filters.get('sizes'):
                # Filter by size if product has size info
                filtered_products = []
                for product in products:
                    # Assume size info is in product description or separate field
                    product_sizes = advanced_filters['sizes']
                    # For now, include all products (would need proper size field in DB)
                    filtered_products.append(product)
                products = filtered_products
            
            if products:
                # Build filter description
                filter_desc = []
                if advanced_filters.get('sizes'):
                    filter_desc.append(f"Size {', '.join(advanced_filters['sizes'])}")
                if advanced_filters.get('max_price'):
                    filter_desc.append(f"Dưới {advanced_filters['max_price']:,.0f} VND")
                if advanced_filters.get('min_price'):
                    filter_desc.append(f"Trên {advanced_filters['min_price']:,.0f} VND")
                if advanced_filters.get('gender'):
                    filter_desc.append(f"Dành cho {advanced_filters['gender']}")

                filter_text = f" ({', '.join(filter_desc)})" if filter_desc else ""
                response_text = f"🛍️ **Tìm thấy {len(products)} sản phẩm phù hợp{filter_text}:**\n\n"
                
                # Show first 3 products in text
                for i, product in enumerate(products[:3], 1):
                    response_text += f"{i}. **{product['name']}**\n"
                    response_text += f"   💰 {product['price']:,.0f} VND\n"
                    response_text += f"   🏷️ {product['brand']} - {product['category']}\n"
                    response_text += f"   👉 [Xem chi tiết](/#/products/{product['id']})\n\n"
                
                if len(products) > 3:
                    response_text += f"...và **{len(products) - 3} sản phẩm khác** bên dưới!"
                
                return {
                    'message': response_text,
                    'suggested_products': products,
                    'quick_replies': ['Xem tất cả', 'Lọc theo giá', 'Tìm khác'],
                    'metadata': {'intent': 'product_search', 'results_count': len(products)}
                }
            else:
                return {
                    'message': 'Xin lỗi, không tìm thấy sản phẩm nào phù hợp. Bạn có thể thử:\n\n• Mô tả chi tiết hơn\n• Tìm theo thương hiệu\n• Xem tất cả sản phẩm',
                    'quick_replies': ['Xem tất cả sản phẩm', 'Thương hiệu phổ biến', 'Hỗ trợ'],
                    'metadata': {'intent': 'product_search', 'results_count': 0}
                }
                
        except Exception as e:
            logger.error(f"Error handling product search: {e}")
            return self._generate_error_response()
    
    def _extract_filters(self, message: str) -> Dict:
        """Extract filters từ message"""
        filters = {}
        
        # Extract brand
        brands = self.db_reader.get_all_brands()
        for brand in brands:
            if brand['title'].lower() in message:
                filters['brand'] = brand['title']
                break
        
        # Extract category
        categories = self.db_reader.get_all_categories()
        for cat in categories:
            if cat['title'].lower() in message:
                filters['category'] = cat['title']
                break
        
        # Extract price range
        price_patterns = [
            r'dưới\s+(\d+)k?',
            r'từ\s+(\d+)k?\s+đến\s+(\d+)k?',
            r'khoảng\s+(\d+)k?'
        ]
        
        for pattern in price_patterns:
            match = re.search(pattern, message)
            if match:
                if len(match.groups()) == 1:
                    price = int(match.group(1)) * 1000
                    if 'dưới' in pattern:
                        filters['max_price'] = price
                    else:
                        filters['min_price'] = price - 100000
                        filters['max_price'] = price + 100000
                elif len(match.groups()) == 2:
                    filters['min_price'] = int(match.group(1)) * 1000
                    filters['max_price'] = int(match.group(2)) * 1000
                break
        
        # Extract color với mapping chi tiết hơn
        color_mapping = {
            'đỏ': ['đỏ', 'red'],
            'xanh dương': ['xanh dương', 'xanh', 'blue', 'navy'],
            'xanh lá': ['xanh lá', 'green'],
            'vàng': ['vàng', 'yellow'],
            'đen': ['đen', 'black'],
            'trắng': ['trắng', 'white'],
            'xám': ['xám', 'gray', 'grey'],
            'nâu': ['nâu', 'brown'],
            'hồng': ['hồng', 'pink'],
            'tím': ['tím', 'purple'],
            'cam': ['cam', 'orange']
        }

        for color_name, keywords in color_mapping.items():
            if any(keyword in message for keyword in keywords):
                filters['color'] = color_name
                break

        # Extract size
        # Tìm size dạng số (36-43)
        size_number_match = re.search(r'\b(3[6-9]|4[0-3])\b', message)
        if size_number_match:
            filters['size'] = size_number_match.group(1)
        else:
            # Tìm size dạng chữ (XS, S, M, L, XL, XXL) với word boundary
            size_patterns = [
                (r'\bxxl\b', 'XXL'),
                (r'\bxl\b', 'XL'),
                (r'\bl\b', 'L'),
                (r'\bm\b', 'M'),
                (r'\bs\b', 'S'),
                (r'\bxs\b', 'XS'),
                (r'\b2xl\b', 'XXL'),
                (r'extra\s+large', 'XL'),
                (r'extra\s+extra\s+large', 'XXL'),
                (r'extra\s+small', 'XS'),
                (r'\blarge\b', 'L'),
                (r'\bmedium\b', 'M'),
                (r'\bsmall\b', 'S')
            ]

            message_lower = message.lower()
            for pattern, size_name in size_patterns:
                if re.search(pattern, message_lower):
                    filters['size'] = size_name
                    break

        return filters
    
    def _handle_stats_request(self, message: str) -> Dict:
        """Xử lý yêu cầu thống kê"""
        try:
            stats = self.db_reader.get_database_stats()
            
            response_text = "📊 **Thống kê Shop:**\n\n"
            
            # Product stats
            response_text += f"🛍️ **Sản phẩm**: {stats['products']['total']}\n"
            response_text += f"💰 **Giá trung bình**: {stats['products']['avg_price']:,.0f} VND\n"
            response_text += f"💸 **Giá thấp nhất**: {stats['products']['min_price']:,.0f} VND\n"
            response_text += f"💎 **Giá cao nhất**: {stats['products']['max_price']:,.0f} VND\n\n"
            
            # Top brands
            response_text += "🏆 **Top Thương hiệu:**\n"
            for brand in stats['brands']['top']:
                response_text += f"• {brand['title']}: {brand['products']} sản phẩm\n"
            
            response_text += "\n🏆 **Top Danh mục:**\n"
            for cat in stats['categories']['top']:
                response_text += f"• {cat['name']}: {cat['products']} sản phẩm\n"
            
            return {
                'message': response_text,
                'quick_replies': ['Chi tiết thương hiệu', 'Chi tiết danh mục', 'Sản phẩm bán chạy'],
                'metadata': {'intent': 'stats_request', 'type': 'overview'}
            }
            
        except Exception as e:
            logger.error(f"Error handling stats request: {e}")
            return self._generate_error_response()
    
    def _handle_recommendation(self, message: str, user=None) -> Dict:
        """Xử lý gợi ý sản phẩm"""
        try:
            # Get random products for recommendation
            products = self.db_reader.search_products("", {})
            
            if products:
                # Get top 5 random products
                import random
                recommended = random.sample(products, min(5, len(products)))
                
                response_text = "💡 **Gợi ý sản phẩm cho bạn:**\n\n"
                
                for i, product in enumerate(recommended[:3], 1):
                    response_text += f"{i}. **{product['name']}**\n"
                    response_text += f"   💰 {product['price']:,.0f} VND\n"
                    response_text += f"   🏷️ {product['brand']} - {product['category']}\n"
                    response_text += f"   👉 [Xem ngay](/#/products/{product['id']})\n\n"
                
                return {
                    'message': response_text,
                    'suggested_products': recommended,
                    'quick_replies': ['Xem thêm gợi ý', 'Tìm theo sở thích', 'Sản phẩm hot'],
                    'metadata': {'intent': 'recommendation', 'count': len(recommended)}
                }
            else:
                return {
                    'message': 'Hiện tại chưa có sản phẩm để gợi ý. Vui lòng quay lại sau!',
                    'quick_replies': ['Xem tất cả sản phẩm', 'Liên hệ hỗ trợ'],
                    'metadata': {'intent': 'recommendation', 'count': 0}
                }
                
        except Exception as e:
            logger.error(f"Error handling recommendation: {e}")
            return self._generate_error_response()
    
    def _handle_general_chat(self, message: str, user=None, detected_intent: str = 'general_chat') -> Dict:
        """Xử lý chat chung với Hybrid AI (Ollama + Gemini)"""
        message_lower = message.lower()

        # Remove old greeting logic - now handled by intent detection

        # Hybrid AI Strategy: Ollama for simple chat, Gemini for complex tasks
        try:
            # Check if this is a simple chat that Ollama can handle
            if self._should_use_ollama(message_lower, detected_intent):
                return self._handle_with_ollama(message, user, detected_intent)
            else:
                return self._handle_with_gemini(message, user, detected_intent)

        except Exception as e:
            logger.error(f"Error in hybrid general chat: {e}")
            return self._handle_general_chat_fallback(message)

    def _should_use_ollama(self, message: str, intent: str) -> bool:
        """Quyết định có nên dùng Ollama không"""

        # Simple emotional expressions - Ollama handles better
        emotional_patterns = [
            'buồn', 'vui', 'hạnh phúc', 'tức giận', 'stress', 'mệt', 'chán',
            'thích', 'ghét', 'yêu', 'cảm ơn', 'xin lỗi', 'tuyệt vời', 'tệ'
        ]

        # Simple greetings and casual chat - Ollama is faster
        casual_patterns = [
            'alo', 'hello', 'hi', 'chào', 'hế lô', 'xin chào',
            'thế nào', 'sao rồi', 'khỏe không', 'làm gì', 'ở đâu'
        ]

        # Simple questions - Ollama can handle
        simple_questions = [
            'tên gì', 'là ai', 'làm gì', 'ở đâu', 'thế nào', 'sao',
            'có phải', 'đúng không', 'thật không'
        ]

        # Size consultation with height/weight - Ollama handles well
        size_consultation_patterns = [
            '1m', 'cao', 'nặng', 'kg', 'size gì', 'cỡ gì', 'mặc size'
        ]

        # Use Ollama for simple cases
        if (any(pattern in message for pattern in emotional_patterns) or
            any(pattern in message for pattern in casual_patterns) or
            any(pattern in message for pattern in simple_questions) or
            any(pattern in message for pattern in size_consultation_patterns) or
            intent in ['greeting', 'goodbye', 'size_inquiry']):
            return True

        # Use Gemini for complex cases (product-related, function calling needed)
        complex_patterns = [
            'sản phẩm', 'mua', 'giá', 'tìm', 'search', 'gợi ý', 'tư vấn',
            'size', 'màu', 'thương hiệu', 'danh mục', 'khuyến mãi'
        ]

        if any(pattern in message for pattern in complex_patterns):
            return False

        # Default: use Ollama for general chat
        return True

    def _handle_with_ollama(self, message: str, user=None, detected_intent: str = 'general_chat') -> Dict:
        """Xử lý với Ollama AI"""
        try:
            from .ollama_service import ollama_service

            if ollama_service.is_available():
                # Enhanced context for Ollama with size consultation
                if detected_intent == 'size_inquiry' or any(pattern in message.lower() for pattern in ['1m', 'cao', 'nặng', 'kg', 'size gì']):
                    context = f"""Bạn là chuyên gia tư vấn size thời trang của shop online.

BẢNG SIZE THAM KHẢO:
- Size S: Cao 1m50-1m60, Nặng 45-55kg
- Size M: Cao 1m60-1m70, Nặng 55-65kg
- Size L: Cao 1m70-1m80, Nặng 65-75kg
- Size XL: Cao 1m80+, Nặng 75kg+

HƯỚNG DẪN TƯ VẤN:
- Dựa vào chiều cao và cân nặng để gợi ý size phù hợp
- Giải thích tại sao chọn size đó
- Đề xuất có thể thử size khác nếu muốn loose/fit hơn
- Trả lời ngắn gọn, tự nhiên bằng tiếng Việt
- KHÔNG dùng markdown formatting

Câu hỏi: {message}"""
                else:
                    context = f"""Bạn là nhân viên tư vấn thân thiện của shop thời trang online.
Trả lời ngắn gọn, tự nhiên bằng tiếng Việt.
KHÔNG dùng markdown formatting.
Giữ tone thân thiện, gần gũi như bạn bè.

Câu hỏi: {message}"""

                ollama_response = ollama_service.generate_response(context)

                if ollama_response.get('success'):
                    # Generate appropriate quick replies
                    quick_replies = self._generate_smart_quick_replies(message, detected_intent)

                    return {
                        'message': ollama_response['message'],
                        'quick_replies': quick_replies,
                        'metadata': {
                            'intent': detected_intent,
                            'ai_provider': 'ollama',
                            'model_used': ollama_response.get('model_used', 'llama3.2'),
                            'response_time': ollama_response.get('response_time', 0)
                        }
                    }

            # Fallback to Gemini if Ollama fails
            logger.warning("Ollama failed, falling back to Gemini")
            return self._handle_with_gemini(message, user, detected_intent)

        except Exception as e:
            logger.error(f"Error with Ollama: {e}")
            return self._handle_with_gemini(message, user, detected_intent)

    def _handle_with_gemini(self, message: str, user=None, detected_intent: str = 'general_chat') -> Dict:
        """Xử lý với Gemini AI"""
        try:
            from .gemini_service import gemini_service

            # Chuẩn bị context cho Gemini
            context = self._prepare_ai_context(user)

            # Gọi Gemini để tạo response với function calling
            gemini_response = gemini_service.generate_response(message, context, user)

            if gemini_response['success']:
                # Xử lý function calls nếu có
                suggested_products = []
                actions_taken = []

                for func_call in gemini_response.get('function_calls', []):
                    if func_call['function'] == 'search_products' and func_call['result'].get('success'):
                        suggested_products = func_call['result']['products']
                        actions_taken.append({
                            'type': 'product_search',
                            'query': func_call['parameters'].get('query'),
                            'results_count': len(suggested_products)
                        })
                    elif func_call['function'] == 'get_shop_stats' and func_call['result'].get('success'):
                        actions_taken.append({
                            'type': 'stats_query',
                            'stats': func_call['result']['stats']
                        })

                # Generate smart quick replies based on message content
                quick_replies = self._generate_smart_quick_replies(message, detected_intent)

                return {
                    'message': gemini_response['message'],
                    'suggested_products': suggested_products,
                    'actions_taken': actions_taken,
                    'quick_replies': quick_replies,
                    'metadata': {
                        'intent': detected_intent,
                        'ai_provider': 'gemini',
                        'model_used': gemini_response.get('model_used'),
                        'response_time': gemini_response.get('response_time'),
                        'function_calls': len(gemini_response.get('function_calls', []))
                    }
                }
            else:
                # Fallback to rule-based response
                logger.warning(f"Gemini failed: {gemini_response.get('error')}, using fallback")
                return self._handle_general_chat_fallback(message)

        except Exception as e:
            logger.error(f"Error in Gemini general chat: {e}")
            return self._handle_general_chat_fallback(message)
    
    def _prepare_ai_context(self, user) -> Dict:
        """Chuẩn bị context cho AI (Gemini) với thông tin shop chi tiết"""
        context = {
            'shop_info': {
                'name': 'Shop Thời Trang Online',
                'products': ['áo thun', 'áo sơ mi', 'quần jean', 'giày thể thao'],
                'price_range': '200k-800k VND',
                'sizes': {
                    'áo': ['S', 'M', 'L', 'XL'],
                    'quần': ['28', '29', '30', '31', '32', '33', '34', '35', '36', '37', '38', '39', '40', '41', '42']
                },
                'size_guide': {
                    'S': 'Cao 1m50-1m60, Nặng 45-55kg',
                    'M': 'Cao 1m60-1m70, Nặng 55-65kg',
                    'L': 'Cao 1m70-1m80, Nặng 65-75kg',
                    'XL': 'Cao 1m80+, Nặng 75kg+'
                },
                'policies': {
                    'return': 'Đổi trả trong 7 ngày',
                    'shipping': 'Giao hàng toàn quốc, phí ship 30k (miễn phí đơn >500k)',
                    'payment': 'Thanh toán COD, chuyển khoản, ví điện tử'
                }
            },
            'instructions': {
                'tone': 'Thân thiện, chuyên nghiệp như nhân viên tư vấn giỏi',
                'language': 'Tiếng Việt tự nhiên, KHÔNG dùng markdown formatting',
                'size_consultation': 'Khi khách hỏi về size và cung cấp chiều cao/cân nặng, hãy tư vấn size cụ thể và giải thích tại sao',
                'general_questions': 'Trả lời câu hỏi chung (thời gian, thời tiết, etc.) một cách bình thường như AI assistant',
                'ending': 'Luôn kết thúc bằng câu hỏi hoặc gợi ý tiếp theo để duy trì cuộc trò chuyện',
                'natural_conversation': 'QUAN TRỌNG: Trò chuyện tự nhiên như con người, KHÔNG bao giờ nhắc đến "gọi hàm", "function", "search_products" hay thuật ngữ kỹ thuật. Chỉ nói "mình sẽ tìm kiếm cho bạn" hoặc "để mình kiểm tra"'
            }
        }

        if user and user.is_authenticated:
            context['user_name'] = user.get_full_name() or user.username

            # Lấy preferences của user nếu có
            try:
                from .models import UserPreference
                prefs = UserPreference.objects.filter(user=user).first()
                if prefs:
                    context['user_preferences'] = {
                        'preferred_categories': prefs.preferred_categories,
                        'preferred_brands': prefs.preferred_brands,
                        'size_preferences': prefs.size_preferences,
                        'price_range': prefs.price_range
                    }
            except Exception as e:
                logger.warning(f"Could not load user preferences: {e}")

        return context

    def _generate_smart_quick_replies(self, message: str, intent: str) -> list:
        """Tạo quick replies thông minh dựa trên message và intent"""
        message_lower = message.lower()

        # Size consultation replies
        if any(word in message_lower for word in ['size', 'cỡ', 'kích thước', '1m', 'kg', 'cao', 'nặng']):
            return ['Tư vấn size áo', 'Tư vấn size quần', 'Bảng size chi tiết', 'Đo size']

        # Price inquiry replies
        elif any(word in message_lower for word in ['giá', 'bao nhiêu', 'tiền', 'chi phí']):
            return ['Xem giá áo thun', 'Xem giá quần jean', 'So sánh giá', 'Khuyến mãi']

        # Time/date replies
        elif any(word in message_lower for word in ['ngày', 'tháng', 'thời gian', 'hôm nay', 'ngày mai']):
            return ['Xem lịch khuyến mãi', 'Thời tiết hôm nay', 'Sản phẩm mới', 'Hỗ trợ khác']

        # Weather replies
        elif any(word in message_lower for word in ['thời tiết', 'nắng', 'mưa', 'lạnh', 'nóng']):
            return ['Outfit cho thời tiết', 'Áo mùa hè', 'Áo mùa đông', 'Tư vấn phối đồ']

        # Greeting replies
        elif any(word in message_lower for word in ['chào', 'hello', 'hi']):
            return ['🛍️ Tìm sản phẩm', '🔥 Sản phẩm hot', '💰 Khuyến mãi', '📏 Tư vấn size']

        # Policy replies
        elif any(word in message_lower for word in ['chính sách', 'đổi trả', 'bảo hành', 'ship']):
            return ['Chính sách đổi trả', 'Phí vận chuyển', 'Thanh toán', 'Bảo hành']

        # Product search replies
        elif any(word in message_lower for word in ['áo', 'quần', 'giày', 'tìm', 'mua']):
            return ['Áo thun', 'Quần jean', 'Giày thể thao', 'Xem tất cả']

        # Default replies for general chat
        else:
            return ['Tìm sản phẩm', 'Tư vấn size', 'Xem khuyến mãi', 'Hỗ trợ']

    def _is_quick_reply_action(self, message: str) -> bool:
        """Kiểm tra xem message có phải là quick reply action không"""
        quick_reply_actions = [
            'bảng size chi tiết', 'tư vấn size', 'tư vấn size áo', 'tư vấn size quần', 'đo size',
            'sản phẩm hot', '🔥 sản phẩm hot', 'khuyến mãi', '💰 khuyến mãi',
            'xem giá áo thun', 'xem giá quần jean', 'so sánh giá',
            'chính sách đổi trả', 'phí vận chuyển', 'thanh toán', 'bảo hành',
            'áo thun', 'quần jean', 'giày thể thao', 'xem tất cả',
            'tìm sản phẩm', '🛍️ tìm sản phẩm', 'hỗ trợ'
        ]

        return message.lower().strip() in quick_reply_actions

    def _handle_quick_reply_action(self, message: str, user=None) -> Dict:
        """Xử lý quick reply actions"""
        action = message.lower().strip()

        # Size guide actions
        if action in ['bảng size chi tiết', 'đo size']:
            return {
                'message': """📏 **BẢNG SIZE CHI TIẾT**

**ÁO (S, M, L, XL):**
• Size S: Cao 1m50-1m60, Nặng 45-55kg
• Size M: Cao 1m60-1m70, Nặng 55-65kg
• Size L: Cao 1m70-1m80, Nặng 65-75kg
• Size XL: Cao 1m80+, Nặng 75kg+

**QUẦN (28-42):**
• Size 28-30: Vòng eo 70-76cm
• Size 31-33: Vòng eo 78-84cm
• Size 34-36: Vòng eo 86-92cm
• Size 37-42: Vòng eo 94-107cm

**LƯU Ý:** Size có thể thay đổi tùy theo chất liệu và form dáng sản phẩm.""",
                'quick_replies': ['Tư vấn size cá nhân', 'Xem sản phẩm', 'Hỗ trợ thêm'],
                'intent': 'size_guide'
            }

        # Size consultation
        elif action in ['tư vấn size', 'tư vấn size cá nhân']:
            return {
                'message': """📏 **TƯ VẤN SIZE CÁ NHÂN**

Để tư vấn size chính xác nhất cho bạn, mình cần biết:

🔸 **Chiều cao** (ví dụ: 1m65)
🔸 **Cân nặng** (ví dụ: 56kg)
🔸 **Loại sản phẩm** muốn mua (áo thun, áo sơ mi, quần jean, v.v.)

**Ví dụ:** "Tôi cao 1m65, nặng 56kg, muốn mua áo thun"

Bạn hãy cho mình biết thông tin này để mình tư vấn size phù hợp nhất nhé! 😊""",
                'quick_replies': ['Bảng size chi tiết', 'Áo thun', 'Quần jean', 'Hỗ trợ khác'],
                'intent': 'size_consultation'
            }

        # Hot products
        elif action in ['sản phẩm hot', '🔥 sản phẩm hot']:
            products = self.db_reader.get_trending_products(limit=5)
            if products:
                message_text = "🔥 **SẢN PHẨM HOT NHẤT:**\n\n"
                for i, product in enumerate(products, 1):
                    message_text += f"{i}. **{product['name']}** - {product['price']:,.0f} VND\n"

                return {
                    'message': message_text,
                    'suggested_products': products,
                    'quick_replies': ['Xem chi tiết', 'Thêm vào giỏ', 'Tìm tương tự'],
                    'intent': 'hot_products'
                }
            else:
                return {
                    'message': '🔥 **SẢN PHẨM HOT:**\n\nHiện tại chúng mình đang cập nhật danh sách sản phẩm hot. Bạn có thể xem tất cả sản phẩm hoặc tìm kiếm theo danh mục nhé!',
                    'quick_replies': ['Xem tất cả sản phẩm', 'Áo thun', 'Quần jean', 'Giày'],
                    'intent': 'hot_products'
                }

        # Promotions
        elif action in ['khuyến mãi', '💰 khuyến mãi']:
            return {
                'message': """💰 **KHUYẾN MÃI HOT:**

🎉 **Ưu đãi đang diễn ra:**
• Miễn phí ship đơn hàng từ 500k
• Giảm 10% cho khách hàng mới
• Mua 2 tặng 1 cho áo thun
• Combo 3 sản phẩm giảm 15%

📅 **Thời gian:** Đến hết tháng này
🎁 **Quà tặng:** Sticker và túi xách thời trang""",
                'quick_replies': ['Áp dụng ngay', 'Xem điều kiện', 'Sản phẩm khuyến mãi'],
                'intent': 'promotions'
            }

        # Product categories
        elif action in ['áo thun', 'quần jean', 'giày thể thao']:
            return self._handle_product_search(action, action)

        # General help
        elif action in ['hỗ trợ', 'tìm sản phẩm', '🛍️ tìm sản phẩm']:
            return {
                'message': '🤝 **HỖ TRỢ KHÁCH HÀNG:**\n\nMình có thể giúp bạn:\n• Tìm kiếm sản phẩm\n• Tư vấn size\n• Thông tin khuyến mãi\n• Chính sách shop\n• Trả lời mọi câu hỏi\n\nBạn cần hỗ trợ gì nhé?',
                'quick_replies': ['Tìm sản phẩm', 'Tư vấn size', 'Khuyến mãi', 'Chính sách'],
                'intent': 'help'
            }

        # Default fallback
        else:
            return self._handle_general_chat(message, user, 'general_chat')

    def _handle_general_chat_fallback(self, message: str) -> Dict:
        """Fallback response khi cả Ollama và Gemini đều không khả dụng"""
        message_lower = message.lower()

        # Simple pattern matching for common cases
        if any(word in message_lower for word in ['buồn', 'buồn qá', 'sad', 'tệ']):
            return {
                'message': 'Ôi không! Tại sao bạn lại buồn vậy? 😢 Có phải vì không tìm được sản phẩm ưng ý không? Để mình giúp bạn tìm những món đồ đẹp để tâm trạng tốt hơn nhé! ✨',
                'quick_replies': ['🛍️ Tìm sản phẩm', '🔥 Sản phẩm hot', '💰 Khuyến mãi', '😊 Động viên'],
                'metadata': {'intent': 'emotional_support'}
            }

        elif any(word in message_lower for word in ['vui', 'hạnh phúc', 'happy', 'tuyệt']):
            return {
                'message': 'Thật tuyệt khi bạn vui vẻ! 😊 Hãy để mình chia sẻ niềm vui này bằng cách giúp bạn tìm những sản phẩm thời trang đẹp nhé! ✨',
                'quick_replies': ['🛍️ Mua sắm vui', '🔥 Sản phẩm hot', '💰 Ưu đãi', '📏 Tư vấn size'],
                'metadata': {'intent': 'positive_emotion'}
            }

        elif any(word in message_lower for word in ['chào', 'hello', 'hi', 'xin chào']):
            return {
                'message': 'Xin chào bạn! 👋 Chào mừng bạn đến với shop thời trang của chúng mình! Mình có thể giúp bạn tìm sản phẩm, tư vấn size, hoặc trả lời mọi câu hỏi. Bạn cần hỗ trợ gì nhé? 😊',
                'quick_replies': ['🛍️ Tìm sản phẩm', '📏 Tư vấn size', '💰 Khuyến mãi', '❓ Hỗ trợ'],
                'metadata': {'intent': 'greeting_fallback'}
            }

        elif any(word in message_lower for word in ['thế nào', 'sao rồi', 'như thế nào']):
            return {
                'message': 'Mọi thứ đều tốt! 😊 Shop đang có nhiều sản phẩm mới và ưu đãi hấp dẫn đấy! Bạn muốn xem gì không?',
                'quick_replies': ['🆕 Sản phẩm mới', '🔥 Sản phẩm hot', '💰 Ưu đãi', '🛍️ Tìm kiếm'],
                'metadata': {'intent': 'casual_chat'}
            }

        elif any(word in message_lower for word in ['cảm ơn', 'thanks', 'thank you']):
            return {
                'message': 'Không có gì! 😊 Rất vui được hỗ trợ bạn! Nếu cần thêm gì, cứ hỏi mình nhé!',
                'quick_replies': ['🛍️ Tiếp tục mua sắm', '📞 Liên hệ', '❓ Hỗ trợ khác', '👋 Tạm biệt'],
                'metadata': {'intent': 'thanks'}
            }

        else:
            # Default fallback
            return {
                'message': 'Xin lỗi, mình không hiểu rõ câu hỏi của bạn. Nhưng mình có thể giúp bạn tìm sản phẩm, tư vấn size, xem khuyến mãi hoặc trả lời câu hỏi về shop. Bạn muốn làm gì nhé? 😊',
                'quick_replies': ['🛍️ Tìm sản phẩm', '📏 Tư vấn size', '💰 Khuyến mãi', '❓ Hỗ trợ'],
                'metadata': {'intent': 'general_fallback'}
            }

    def _generate_error_response(self) -> Dict:
        """Tạo response khi có lỗi"""
        return {
            'message': 'Xin lỗi, có lỗi xảy ra. Tôi vẫn có thể giúp bạn:\n\n🔍 Tìm sản phẩm\n📊 Xem thống kê\n💬 Trò chuyện chung',
            'quick_replies': ['Tìm sản phẩm', 'Thống kê', 'Thử lại'],
            'metadata': {'intent': 'error'}
        }


# Global instance
smart_ai = SmartAIProcessor()

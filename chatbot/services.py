"""
AI Chatbot Services - Xử lý logic thông minh cho chatbot
"""
import re
import json
import unicodedata
from django.db.models import Q
from api.models import Product, Order, Favorite, Category, SubCategory, SizeGuide
from api.serializers import ProductSerializer, OrderSerializer
import ollama


class SmartChatbotService:
    """Service xử lý chatbot thông minh"""
    
    def __init__(self, user):
        self.user = user

    def clean_text_for_db(self, text):
        """Clean text để tránh lỗi MySQL encoding với emoji"""
        if not text:
            return text

        # Remove emoji và special characters có thể gây lỗi MySQL
        try:
            # Test encoding
            text.encode('utf-8').decode('utf-8')
            # Remove 4-byte UTF-8 characters (emoji)
            cleaned = ''.join(char for char in text if ord(char) < 65536)
            return cleaned
        except (UnicodeError, ValueError):
            # Fallback: chỉ giữ ASCII và basic UTF-8
            return ''.join(char for char in text if ord(char) < 1000)

    def clean_markdown_formatting(self, text):
        """Remove markdown formatting từ text"""
        if not text:
            return text

        # Remove markdown formatting
        import re

        # Remove **bold** formatting
        text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)

        # Remove *italic* formatting
        text = re.sub(r'\*(.*?)\*', r'\1', text)

        # Remove __underline__ formatting
        text = re.sub(r'__(.*?)__', r'\1', text)

        # Remove _italic_ formatting
        text = re.sub(r'_(.*?)_', r'\1', text)

        # Remove ### headers
        text = re.sub(r'^#{1,6}\s*', '', text, flags=re.MULTILINE)

        # Remove ``` code blocks
        text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)

        # Remove ` inline code `
        text = re.sub(r'`(.*?)`', r'\1', text)

        # Remove [link](url) formatting, keep only text
        text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)

        return text.strip()

    def analyze_message(self, message):
        """Phân tích tin nhắn để xác định intent"""
        message_lower = message.lower().strip()
        
        # Intent 1: Personal size recommendation (ưu tiên cao nhất)
        import re
        # Pattern mới hỗ trợ 1m56, 1.56m, 156cm, 56kg
        height_weight_patterns = [
            r'(\d+)m(\d+).*?(\d+(?:\.\d+)?)\s*kg',  # 1m56 60kg
            r'(\d+(?:\.\d+)?)\s*(?:m|cm).*?(\d+(?:\.\d+)?)\s*kg',  # 156cm 60kg hoặc 1.56m 60kg
            r'(\d+(?:\.\d+)?)\s*kg.*?(\d+)m(\d+)',  # 60kg 1m56
            r'(\d+(?:\.\d+)?)\s*kg.*?(\d+(?:\.\d+)?)\s*(?:m|cm)',  # 60kg 156cm
        ]

        for pattern in height_weight_patterns:
            if re.search(pattern, message_lower):
                return {
                    'intent': 'personal_size_recommendation',
                    'confidence': 0.95
                }

        # Intent 2: Size guide (ưu tiên cao)
        size_keywords = ['size', 'kích cỡ', 'kích thước', 'hướng dẫn size', 'bảng size', 'chọn size', 'size nào', 'mặc size']
        # Exclude if it's a product search with size mention
        if any(keyword in message_lower for keyword in size_keywords) and not any(word in message_lower for word in ['tìm', 'có', 'xem', 'show']):
            return {
                'intent': 'size_guide',
                'confidence': 0.9
            }

        # Intent 3: Tìm kiếm sản phẩm (ưu tiên cao hơn price filter)
        product_keywords = {
            'áo': ['áo', 'shirt', 'top', 'blouse', 'hoodie', 'sweater'],
            'quần': ['quần', 'pants', 'jeans', 'shorts', 'trouser'],
            'giày': ['giày', 'shoes', 'sneaker', 'boot'],
            'túi': ['túi', 'bag', 'backpack', 'handbag'],
            'phụ kiện': ['phụ kiện', 'accessory', 'belt', 'hat', 'cap']
        }

        for category, keywords in product_keywords.items():
            if any(keyword in message_lower for keyword in keywords):
                # Tìm subcategory chi tiết hơn
                subcategory = self.find_matching_subcategory(message_lower, category)
                return {
                    'intent': 'search_product',
                    'category': category,
                    'subcategory': subcategory,
                    'keywords': keywords
                }

        # Intent 4: Price filter (ưu tiên thấp hơn product search)
        price_keywords = ['giá', 'price', 'dưới', 'trên', 'từ', 'đến', 'k', '000', 'rẻ', 'mắc', 'tiền']
        # Chỉ trigger nếu không có product keywords
        has_product_keywords = any(keyword in message_lower for category_keywords in [
            ['áo', 'shirt', 'top', 'blouse', 'hoodie', 'sweater'],
            ['quần', 'pants', 'jeans', 'shorts', 'trouser'],
            ['giày', 'shoes', 'sneaker', 'boot'],
            ['túi', 'bag', 'backpack', 'handbag']
        ] for keyword in category_keywords)

        if any(keyword in message_lower for keyword in price_keywords) and not has_product_keywords:
            return {
                'intent': 'price_filter',
                'confidence': 0.7
            }

        # Intent 5: Hướng dẫn đặt hàng
        order_guide_keywords = ['cách đặt hàng', 'làm sao đặt hàng', 'hướng dẫn đặt hàng', 'đặt hàng như thế nào', 'quy trình đặt hàng']
        if any(keyword in message_lower for keyword in order_guide_keywords):
            return {
                'intent': 'order_guide',
                'confidence': 0.9
            }

        # Intent 6: Tra cứu đơn hàng
        order_keywords = ['đơn hàng', 'order', 'đặt hàng', 'mua', 'đã đặt', 'đã mua']
        if any(keyword in message_lower for keyword in order_keywords):
            return {
                'intent': 'check_orders',
                'keywords': order_keywords
            }

        # Intent 7: Sản phẩm yêu thích
        favorite_keywords = ['yêu thích', 'favorite', 'thích', 'wishlist', 'saved']
        if any(keyword in message_lower for keyword in favorite_keywords):
            return {
                'intent': 'show_favorites',
                'keywords': favorite_keywords
            }
        
        # Intent 8: Chat thông thường
        return {
            'intent': 'general_chat',
            'message': message
        }

    def find_matching_subcategory(self, message_lower, category=None):
        """Tìm subcategory phù hợp với message"""
        # Lấy subcategories theo category nếu có
        if category:
            subcategories = SubCategory.objects.filter(category__title__icontains=category)
        else:
            subcategories = SubCategory.objects.all()

        # Tìm exact match trước (ưu tiên cao nhất)
        for subcategory in subcategories:
            # Check exact title match
            if subcategory.title.lower() in message_lower:
                return subcategory

            # Check exact keyword match
            keywords = subcategory.get_keywords_list()
            for keyword in keywords:
                if keyword in message_lower:
                    return subcategory

        return None
    
    def search_products(self, category, message, subcategory=None):
        """Tìm kiếm sản phẩm theo category và subcategory"""
        try:
            # Check if message contains price filter
            import re
            price_keywords = ['dưới', 'trên', 'từ', 'đến', 'triệu', 'k', 'giá']
            has_price = any(keyword in message.lower() for keyword in price_keywords)

            if has_price:
                # Delegate to price search function for better price handling
                price_result = self.search_products_by_price(message)

                # If price search found products, return with category context
                if price_result['type'] == 'product_list':
                    # Add category/subcategory context to message
                    if subcategory:
                        price_result['message'] = f"Tìm thấy {price_result['count']} {subcategory.title} trong khoảng giá yêu cầu:\n\n" + price_result['message'].split('\n\n', 1)[-1]
                        price_result['subcategory'] = subcategory.title
                    else:
                        price_result['message'] = f"Tìm thấy {price_result['count']} sản phẩm {category} trong khoảng giá yêu cầu:\n\n" + price_result['message'].split('\n\n', 1)[-1]
                        price_result['category_filter'] = category

                return price_result

            # Nếu có subcategory, ưu tiên tìm theo subcategory
            if subcategory:
                products = Product.objects.filter(
                    subcategory=subcategory,
                    countInStock__gt=0
                ).order_by('-createdAt')[:6]

                if products.exists():
                    serializer = ProductSerializer(products, many=True)
                    return {
                        'type': 'product_list',
                        'message': f"Đây là những {subcategory.title} hot nhất hiện tại:",
                        'products': serializer.data,
                        'count': products.count(),
                        'subcategory': subcategory.title
                    }
                else:
                    # Không có sản phẩm trong subcategory cụ thể
                    return {
                        'type': 'no_products',
                        'message': f"Hiện tại shop chưa có {subcategory.title} nào. Bạn có thể xem các sản phẩm khác hoặc liên hệ để được tư vấn thêm! 😊",
                        'subcategory': subcategory.title
                    }

            # Nếu chỉ hỏi "áo" → lọc tất cả sản phẩm có chữ "áo" trong tên
            if category == 'áo':
                products = Product.objects.filter(
                    name__icontains='áo',
                    countInStock__gt=0
                ).order_by('-createdAt')[:6]

                if products.exists():
                    serializer = ProductSerializer(products, many=True)
                    return {
                        'type': 'product_list',
                        'message': f"Đây là tất cả sản phẩm áo hiện có:",
                        'products': serializer.data,
                        'count': products.count(),
                        'category_filter': 'áo'
                    }

            # Tương tự cho quần
            if category == 'quần':
                products = Product.objects.filter(
                    name__icontains='quần',
                    countInStock__gt=0
                ).order_by('-createdAt')[:6]

                if products.exists():
                    serializer = ProductSerializer(products, many=True)
                    return {
                        'type': 'product_list',
                        'message': f"Đây là tất cả sản phẩm quần hiện có:",
                        'products': serializer.data,
                        'count': products.count(),
                        'category_filter': 'quần'
                    }

            # Fallback: Tìm category trong database
            category_obj = Category.objects.filter(
                Q(title__icontains=category) |
                Q(title__icontains='áo') if category == 'áo' else Q() |
                Q(title__icontains='quần') if category == 'quần' else Q() |
                Q(title__icontains='giày') if category == 'giày' else Q() |
                Q(title__icontains='túi') if category == 'túi' else Q()
            ).first()
            
            if not category_obj:
                return {
                    'type': 'no_products',
                    'message': f"Xin lỗi, hiện tại shop chưa có sản phẩm {category} nào. Bạn có thể xem các sản phẩm khác nhé! 😊"
                }
            
            # Lấy sản phẩm theo category
            products = Product.objects.filter(
                category=category_obj,
                countInStock__gt=0  # Chỉ lấy sản phẩm còn hàng
            ).order_by('-createdAt')[:6]  # Giới hạn 6 sản phẩm
            
            if not products.exists():
                return {
                    'type': 'no_products',
                    'message': f"Hiện tại không có {category} nào còn hàng. Vui lòng quay lại sau nhé! 😊"
                }
            
            # Serialize products
            serializer = ProductSerializer(products, many=True)
            
            return {
                'type': 'product_list',
                'message': f"Đây là những {category} hot nhất hiện tại:",
                'products': serializer.data,
                'count': products.count()
            }
            
        except Exception as e:
            return {
                'type': 'error',
                'message': f"Có lỗi xảy ra khi tìm kiếm sản phẩm: {str(e)}"
            }
    
    def get_user_orders(self):
        """Lấy đơn hàng của user"""
        try:
            orders = Order.objects.filter(user=self.user).order_by('-createdAt')[:5]
            
            if not orders.exists():
                return {
                    'type': 'no_orders',
                    'message': "Bạn chưa có đơn hàng nào. Hãy mua sắm ngay để trải nghiệm dịch vụ của chúng tôi! 🛍️"
                }
            
            serializer = OrderSerializer(orders, many=True)
            
            return {
                'type': 'order_list',
                'message': "Đây là các đơn hàng gần đây của bạn:",
                'orders': serializer.data,
                'count': orders.count()
            }
            
        except Exception as e:
            return {
                'type': 'error',
                'message': f"Có lỗi xảy ra khi tra cứu đơn hàng: {str(e)}"
            }
    
    def get_user_favorites(self):
        """Lấy sản phẩm yêu thích của user"""
        try:
            favorites = Favorite.objects.filter(user=self.user).order_by('-created_at')[:6]
            
            if not favorites.exists():
                return {
                    'type': 'no_favorites',
                    'message': "Bạn chưa có sản phẩm yêu thích nào. Hãy thêm sản phẩm vào danh sách yêu thích để dễ dàng tìm lại! ❤️"
                }
            
            products = [fav.product for fav in favorites]
            serializer = ProductSerializer(products, many=True)
            
            return {
                'type': 'favorite_list',
                'message': "Đây là những sản phẩm bạn đã yêu thích:",
                'products': serializer.data,
                'count': favorites.count()
            }
            
        except Exception as e:
            return {
                'type': 'error',
                'message': f"Có lỗi xảy ra khi lấy sản phẩm yêu thích: {str(e)}"
            }
    
    def general_chat(self, message, model='llama3.2:3b'):
        """Chat thông thường với AI"""
        try:
            # System prompt cho shopping assistant
            system_prompt = f"""Bạn là một trợ lý mua sắm thông minh và thân thiện của shop thời trang.
            Hãy trả lời một cách vui vẻ, hữu ích và chuyên nghiệp.

            QUAN TRỌNG:
            - KHÔNG sử dụng markdown formatting như **bold**, *italic*, __underline__
            - KHÔNG sử dụng ### headers, ``` code blocks, hoặc `inline code`
            - Chỉ sử dụng text thuần với emoji và dấu câu bình thường
            - Sử dụng dấu gạch đầu dòng (-) thay vì markdown lists

            Thông tin về user: {self.user.username}

            Nếu user hỏi về:
            - Sản phẩm cụ thể: Gợi ý họ nói "tìm áo" hoặc "tìm quần" để xem sản phẩm
            - Đơn hàng: Gợi ý họ nói "đơn hàng của tôi" để xem chi tiết
            - Yêu thích: Gợi ý họ nói "sản phẩm yêu thích" để xem danh sách

            Hãy trả lời ngắn gọn, thân thiện và có emoji phù hợp."""
            
            response = ollama.chat(
                model=model,
                messages=[
                    {'role': 'system', 'content': system_prompt},
                    {'role': 'user', 'content': message}
                ]
            )
            
            # Clean response trước khi return
            cleaned_response = self.clean_text_for_db(response['message']['content'])
            # Remove markdown formatting
            cleaned_response = self.clean_markdown_formatting(cleaned_response)

            return {
                'type': 'general_response',
                'message': cleaned_response
            }
            
        except Exception as e:
            return {
                'type': 'error',
                'message': f"Xin lỗi, tôi đang gặp một chút vấn đề. Vui lòng thử lại sau! 😅"
            }
    
    def process_message(self, message, model='llama3.2:3b'):
        """Xử lý tin nhắn chính"""
        # Clean message trước khi xử lý
        message = self.clean_text_for_db(message)

        # Phân tích intent
        intent_data = self.analyze_message(message)
        
        # Xử lý theo intent
        if intent_data['intent'] == 'search_product':
            return self.search_products(
                intent_data['category'],
                message,
                subcategory=intent_data.get('subcategory')
            )
        
        elif intent_data['intent'] == 'check_orders':
            return self.get_user_orders()
        
        elif intent_data['intent'] == 'show_favorites':
            return self.get_user_favorites()

        elif intent_data['intent'] == 'size_guide':
            return self.get_size_guide(message)

        elif intent_data['intent'] == 'personal_size_recommendation':
            return self.get_personal_size_recommendation(message)

        elif intent_data['intent'] == 'price_filter':
            return self.search_products_by_price(message)

        elif intent_data['intent'] == 'order_guide':
            return self.get_order_guide()

        else:  # general_chat
            return self.general_chat(message, model)

    def get_size_guide(self, message):
        """Lấy hướng dẫn size cho sản phẩm"""
        try:
            # Tìm subcategory từ message
            subcategory = self.find_matching_subcategory(message.lower())

            if not subcategory:
                return {
                    'type': 'size_guide',
                    'message': """📏 Hướng dẫn chọn size tổng quát:

Áo Thun:
- Size S: 150-160cm, 45-55kg
- Size M: 160-170cm, 55-65kg
- Size L: 170-175cm, 65-75kg
- Size XL: 175-180cm, 75-85kg

Lưu ý: Hãy cho tôi biết bạn muốn xem size guide cho loại sản phẩm nào cụ thể để được tư vấn chính xác hơn! 😊

Hoặc bạn có thể cho tôi biết chiều cao và cân nặng để tôi tư vấn size phù hợp nhất!"""
                }

            # Lấy size guides cho subcategory
            size_guides = SizeGuide.objects.filter(subcategory=subcategory).order_by('size__order')

            if not size_guides.exists():
                return {
                    'type': 'size_guide',
                    'message': f"📏 Size Guide cho {subcategory.title}:\n\nHiện tại chưa có bảng size chi tiết cho {subcategory.title}. Vui lòng liên hệ shop để được tư vấn size phù hợp! 😊"
                }

            # Tạo size guide message
            guide_message = f"📏 Size Guide cho {subcategory.title}:\n\n"

            for guide in size_guides:
                guide_message += f"Size {guide.size.name}:\n"
                if guide.get_height_range():
                    guide_message += f"• Chiều cao: {guide.get_height_range()}\n"
                if guide.get_weight_range():
                    guide_message += f"• Cân nặng: {guide.get_weight_range()}\n"
                if guide.chest:
                    guide_message += f"• Vòng ngực: {guide.chest}cm\n"
                if guide.waist:
                    guide_message += f"• Vòng eo: {guide.waist}cm\n"
                if guide.notes:
                    guide_message += f"• Ghi chú: {guide.notes}\n"
                guide_message += "\n"

            guide_message += "💡 Lưu ý: Đây là size guide tham khảo. Nếu bạn có thắc mắc về size, hãy cho tôi biết chiều cao và cân nặng để được tư vấn cụ thể hơn! 😊"

            return {
                'type': 'size_guide',
                'message': guide_message,
                'subcategory': subcategory.title
            }

        except Exception as e:
            return {
                'type': 'error',
                'message': f"Có lỗi xảy ra khi lấy size guide: {str(e)}"
            }

    def get_personal_size_recommendation(self, message):
        """Tư vấn size cá nhân dựa trên chiều cao và cân nặng"""
        try:
            import re

            # Extract height and weight from message với teen code support
            height = None
            weight = None

            # Pattern 1: Teen code format 1m56 = 156cm
            teen_pattern = r'(\d+)m(\d+).*?(\d+(?:\.\d+)?)\s*kg'
            match = re.search(teen_pattern, message.lower())
            if match:
                meter = int(match.group(1))
                cm = int(match.group(2))
                height = meter * 100 + cm  # 1m56 = 156cm
                weight = float(match.group(3))

            # Pattern 2: Reverse teen code - weight first
            if not height:
                teen_reverse_pattern = r'(\d+(?:\.\d+)?)\s*kg.*?(\d+)m(\d+)'
                match = re.search(teen_reverse_pattern, message.lower())
                if match:
                    weight = float(match.group(1))
                    meter = int(match.group(2))
                    cm = int(match.group(3))
                    height = meter * 100 + cm

            # Pattern 3: Standard format
            if not height:
                standard_patterns = [
                    r'(\d+(?:\.\d+)?)\s*(?:cm).*?(\d+(?:\.\d+)?)\s*kg',  # 156cm 60kg
                    r'(\d+(?:\.\d+)?)\s*(?:m).*?(\d+(?:\.\d+)?)\s*kg',   # 1.56m 60kg
                    r'(\d+(?:\.\d+)?)\s*kg.*?(\d+(?:\.\d+)?)\s*(?:cm)',  # 60kg 156cm
                    r'(\d+(?:\.\d+)?)\s*kg.*?(\d+(?:\.\d+)?)\s*(?:m)'    # 60kg 1.56m
                ]

                for pattern in standard_patterns:
                    match = re.search(pattern, message.lower())
                    if match:
                        if 'kg.*?cm' in pattern or 'kg.*?m' in pattern:  # weight first
                            weight = float(match.group(1))
                            height_val = float(match.group(2))
                            height = height_val * 100 if height_val < 10 else height_val
                        else:  # height first
                            height_val = float(match.group(1))
                            height = height_val * 100 if height_val < 10 else height_val
                            weight = float(match.group(2))
                        break

            if not height or not weight:
                return {
                    'type': 'size_guide',
                    'message': "Để tư vấn size chính xác, bạn vui lòng cho tôi biết chiều cao và cân nặng của bạn nhé! Ví dụ: 'Tôi 1m56 56kg' hoặc 'cao 165cm nặng 60kg'"
                }

            # Find recommended size
            recommended_size = self.recommend_size_for_person(height, weight)

            # Get subcategory from message if possible
            subcategory = self.find_matching_subcategory(message.lower())

            response_message = f"📏 Tư vấn size cho bạn (cao {height:.0f}cm, nặng {weight:.0f}kg):\n\n"

            if subcategory:
                response_message += f"Cho {subcategory.title}: Size {recommended_size['size']}\n"
                response_message += f"Lý do: {recommended_size['reason']}\n\n"

                # Show size guide for this subcategory
                size_guides = SizeGuide.objects.filter(subcategory=subcategory).order_by('size__order')
                if size_guides.exists():
                    response_message += f"Bảng size {subcategory.title}:\n"
                    for guide in size_guides:
                        marker = "👉 " if guide.size.name == recommended_size['size'] else "   "
                        response_message += f"{marker}Size {guide.size.name}: {guide.get_height_range()}, {guide.get_weight_range()}\n"
            else:
                response_message += f"Tổng quát: Size {recommended_size['size']}\n"
                response_message += f"Lý do: {recommended_size['reason']}\n\n"
                response_message += "Hãy cho tôi biết bạn muốn mua loại sản phẩm gì (áo thun, áo sơ mi, quần...) để được tư vấn cụ thể hơn!"

            response_message += f"\n💡 Gợi ý: {recommended_size['note']}"

            return {
                'type': 'personal_size_recommendation',
                'message': response_message,
                'recommended_size': recommended_size['size'],
                'height': height,
                'weight': weight
            }

        except Exception as e:
            return {
                'type': 'error',
                'message': f"Có lỗi xảy ra khi tư vấn size: {str(e)}"
            }

    def recommend_size_for_person(self, height, weight):
        """Recommend size based on height and weight"""
        # Basic size recommendation logic
        if height <= 155 and weight <= 50:
            return {
                'size': 'S',
                'reason': 'Phù hợp với người có thể hình nhỏ',
                'note': 'Nếu thích form rộng có thể chọn size M'
            }
        elif height <= 165 and weight <= 60:
            return {
                'size': 'M',
                'reason': 'Phù hợp với thể hình trung bình',
                'note': 'Size phổ biến nhất, vừa vặn thoải mái'
            }
        elif height <= 175 and weight <= 75:
            return {
                'size': 'L',
                'reason': 'Phù hợp với người cao trung bình',
                'note': 'Nếu thích form ôm có thể thử size M'
            }
        else:
            return {
                'size': 'XL',
                'reason': 'Phù hợp với người có thể hình lớn',
                'note': 'Đảm bảo thoải mái khi mặc'
            }

    def search_products_by_price(self, message):
        """Tìm sản phẩm theo giá"""
        try:
            import re

            # Extract price from message với teen code support
            price_patterns = [
                # Triệu patterns (highest priority)
                r'dưới\s*(\d+(?:\.\d+)?)\s*triệu',           # dưới 2 triệu
                r'trên\s*(\d+(?:\.\d+)?)\s*triệu',           # trên 1 triệu
                r'từ\s*(\d+(?:\.\d+)?)\s*triệu\s*đến\s*(\d+(?:\.\d+)?)\s*triệu',  # từ 1 triệu đến 5 triệu
                r'khoảng\s*(\d+(?:\.\d+)?)\s*triệu',         # khoảng 2 triệu
                r'(\d+(?:\.\d+)?)\s*triệu',                  # 2 triệu

                # Teen code patterns
                r'dưới\s*(\d+)k',                    # dưới 100k
                r'trên\s*(\d+)k',                    # trên 200k
                r'từ\s*(\d+)k\s*đến\s*(\d+)k',      # từ 50k đến 200k
                r'(\d+)k\s*-\s*(\d+)k',             # 100k-300k
                r'khoảng\s*(\d+)k',                 # khoảng 150k
                r'(\d+)k',                          # 100k

                # Standard patterns
                r'dưới\s*(\d+)\.?(\d+)?k',          # dưới 100.5k
                r'dưới\s*(\d+)(?:\.000|000)',       # dưới 100.000
                r'từ\s*(\d+)(?:\.000|000)\s*đến\s*(\d+)(?:\.000|000)',  # từ 100.000 đến 300.000
            ]

            max_price = None
            min_price = None

            for pattern in price_patterns:
                match = re.search(pattern, message.lower())
                if match:
                    # Determine multiplier (triệu = 1,000,000, k = 1,000)
                    multiplier = 1000000 if 'triệu' in pattern else 1000

                    if 'dưới' in pattern:
                        # dưới 2 triệu = dưới 2,000,000
                        max_price = int(float(match.group(1)) * multiplier)
                    elif 'trên' in pattern:
                        # trên 1 triệu = trên 1,000,000
                        min_price = int(float(match.group(1)) * multiplier)
                    elif 'từ' in pattern and 'đến' in pattern:
                        # từ 1 triệu đến 5 triệu = từ 1,000,000 đến 5,000,000
                        min_price = int(float(match.group(1)) * multiplier)
                        max_price = int(float(match.group(2)) * multiplier)
                    elif '-' in pattern:
                        # 100k-300k = 100,000-300,000
                        min_price = int(float(match.group(1)) * multiplier)
                        max_price = int(float(match.group(2)) * multiplier)
                    elif 'khoảng' in pattern:
                        # khoảng 2 triệu = around 2,000,000 (±500k)
                        center_price = int(float(match.group(1)) * multiplier)
                        range_offset = 500000 if multiplier == 1000000 else 50000
                        min_price = center_price - range_offset
                        max_price = center_price + range_offset
                    elif 'triệu' in pattern:
                        # 2 triệu = dưới 2,000,000 (default behavior)
                        max_price = int(float(match.group(1)) * multiplier)
                    elif pattern.endswith('k'):
                        # 100k = dưới 100,000 (default behavior)
                        max_price = int(float(match.group(1)) * multiplier)
                    elif '000' in pattern:
                        # Handle .000 format
                        max_price = int(float(match.group(1)) * multiplier)
                    break

            if not max_price and not min_price:
                return {
                    'type': 'price_filter',
                    'message': "Bạn muốn tìm sản phẩm trong khoảng giá nào? Ví dụ: 'dưới 100k', 'từ 50k đến 200k', 'trên 300k'"
                }

            # Build query
            query = Product.objects.filter(countInStock__gt=0)

            if min_price:
                query = query.filter(price__gte=min_price)
            if max_price:
                query = query.filter(price__lte=max_price)

            # Get category/subcategory if mentioned
            subcategory = self.find_matching_subcategory(message.lower())
            if subcategory:
                query = query.filter(subcategory=subcategory)

            products = query.order_by('price')[:10]

            if not products.exists():
                price_range = ""
                if min_price and max_price:
                    price_range = f"từ {min_price:,}đ đến {max_price:,}đ"
                elif min_price:
                    price_range = f"trên {min_price:,}đ"
                elif max_price:
                    price_range = f"dưới {max_price:,}đ"

                return {
                    'type': 'no_products',
                    'message': f"Hiện tại không có sản phẩm nào trong khoảng giá {price_range}. Bạn có thể thử khoảng giá khác! 😊"
                }

            # Serialize products with price comparison
            serializer = ProductSerializer(products, many=True)
            products_data = serializer.data

            # Add price comparison info
            prices = [float(p['price']) for p in products_data]
            min_found_price = min(prices)
            max_found_price = max(prices)

            price_range_text = ""
            if min_price and max_price:
                price_range_text = f"từ {min_price:,}đ đến {max_price:,}đ"
            elif min_price:
                price_range_text = f"trên {min_price:,}đ"
            elif max_price:
                price_range_text = f"dưới {max_price:,}đ"

            message = f"Tìm thấy {len(products)} sản phẩm trong khoảng giá {price_range_text}:\n\n"
            message += f"💰 Giá thấp nhất: {min_found_price:,.0f}đ\n"
            message += f"💰 Giá cao nhất: {max_found_price:,.0f}đ\n\n"
            message += "Dưới đây là danh sách sản phẩm (sắp xếp theo giá):"

            return {
                'type': 'product_list',
                'message': message,
                'products': products_data,
                'count': len(products),
                'price_filter': {
                    'min_price': min_price,
                    'max_price': max_price,
                    'min_found': min_found_price,
                    'max_found': max_found_price
                }
            }

        except Exception as e:
            return {
                'type': 'error',
                'message': f"Có lỗi xảy ra khi tìm kiếm theo giá: {str(e)}"
            }

    def get_order_guide(self):
        """Hướng dẫn đặt hàng không có markdown"""
        guide_message = """🛍️ Hướng dẫn đặt hàng tại shop thời trang:

1. Chọn sản phẩm: Chọn những sản phẩm yêu thích từ danh mục hàng hóa trên màn hình chính.

2. Đặt sản phẩm vào giỏ hàng: Nhấn nút "Thêm vào giỏ" để thêm sản phẩm vào giỏ hàng.

3. Kiểm tra lại giỏ hàng: Đảm bảo rằng các sản phẩm đã được đặt đúng và số lượng đủ.

4. Đăng nhập/đăng ký tài khoản: Nếu bạn chưa có tài khoản, hãy đăng ký ngay để nhận ưu đãi đặc biệt. Nếu đã có tài khoản, vui lòng đăng nhập.

5. Chọn phương thức thanh toán và giao hàng: Chọn phương thức thanh toán phù hợp (thẻ tín dụng, chuyển khoản ngân hàng) và chọn địa chỉ giao hàng.

6. Xác nhận đơn hàng: Nhấn nút "Đặt hàng" để xác nhận đơn hàng của bạn.

7. Thanh toán và chờ đợi giao hàng: Sau khi đặt hàng, bạn sẽ nhận được thông báo về tình trạng đơn hàng. Chúng tôi sẽ xử lý đơn hàng nhanh chóng nhất có thể.

Nếu bạn cần hỗ trợ thêm hoặc có câu hỏi nào khác, hãy đừng ngần ngại liên hệ với chúng tôi! 😊"""

        return {
            'type': 'order_guide',
            'message': guide_message
        }

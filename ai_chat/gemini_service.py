"""
Google Gemini AI Service for advanced chatbot functionality
Supports function calling, structured responses, and intelligent conversation
"""

import requests
import logging
import json
import time
from typing import Dict, List, Optional, Any
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)


class GeminiService:
    """Advanced AI service using Google Gemini with function calling"""
    
    def __init__(self):
        self.config = getattr(settings, 'GEMINI_CONFIG', {})
        self.api_key = self.config.get('API_KEY', '')
        self.model_name = self.config.get('MODEL', 'gemini-1.5-flash')
        self.temperature = self.config.get('TEMPERATURE', 0.7)
        self.max_tokens = self.config.get('MAX_OUTPUT_TOKENS', 2048)
        self.system_instruction = self.config.get('SYSTEM_INSTRUCTION', '')
        
        # Configure Gemini REST API
        if self.api_key:
            self.base_url = "https://generativelanguage.googleapis.com/v1beta"
            self.model_configured = True
        else:
            logger.error("Gemini API key not configured!")
            self.model_configured = False
            self.base_url = None
    
    def is_available(self) -> bool:
        """Check if Gemini service is available"""
        if not self.api_key or not self.model_configured:
            return False

        cache_key = 'gemini_availability'
        cached_result = cache.get(cache_key)

        if cached_result is not None:
            return cached_result

        try:
            # Test with a simple request using REST API
            url = f"{self.base_url}/models/gemini-1.5-flash:generateContent"
            headers = {
                'Content-Type': 'application/json',
            }
            data = {
                'contents': [{
                    'parts': [{'text': 'Hello'}]
                }],
                'generationConfig': {
                    'maxOutputTokens': 10,
                    'temperature': 0.1
                }
            }

            response = requests.post(
                f"{url}?key={self.api_key}",
                headers=headers,
                json=data,
                timeout=30
            )

            if response.status_code == 200:
                cache.set(cache_key, True, timeout=300)  # Cache for 5 minutes
                return True
            else:
                logger.warning(f"Gemini API returned {response.status_code}: {response.text}")
                cache.set(cache_key, False, timeout=60)
                return False

        except Exception as e:
            logger.warning(f"Gemini service not available: {e}")
            cache.set(cache_key, False, timeout=60)  # Cache failure for 1 minute
            return False
    
    def _get_function_definitions(self) -> List[Dict]:
        """Define functions that Gemini can call"""
        return [
            {
                "name": "search_products",
                "description": "Tìm kiếm sản phẩm trong database shop thời trang",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Từ khóa tìm kiếm (ví dụ: 'áo thun', 'quần jean')"
                        },
                        "category": {
                            "type": "string", 
                            "description": "Danh mục sản phẩm (áo, quần, giày...)"
                        },
                        "price_min": {
                            "type": "number",
                            "description": "Giá tối thiểu (VND)"
                        },
                        "price_max": {
                            "type": "number", 
                            "description": "Giá tối đa (VND)"
                        },
                        "brand": {
                            "type": "string",
                            "description": "Thương hiệu"
                        }
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "get_shop_stats",
                "description": "Lấy thống kê tổng quan về shop (số sản phẩm, thương hiệu, danh mục...)",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "stat_type": {
                            "type": "string",
                            "enum": ["overview", "products", "brands", "categories"],
                            "description": "Loại thống kê cần lấy"
                        }
                    }
                }
            },
            {
                "name": "get_product_recommendations",
                "description": "Lấy gợi ý sản phẩm cho khách hàng",
                "parameters": {
                    "type": "object", 
                    "properties": {
                        "user_preferences": {
                            "type": "object",
                            "description": "Sở thích của user (categories, brands, price_range...)"
                        },
                        "limit": {
                            "type": "number",
                            "description": "Số lượng sản phẩm gợi ý (mặc định 5)"
                        }
                    }
                }
            },
            {
                "name": "check_product_availability",
                "description": "Kiểm tra tình trạng còn hàng của sản phẩm",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "product_id": {
                            "type": "number",
                            "description": "ID của sản phẩm"
                        }
                    },
                    "required": ["product_id"]
                }
            }
        ]
    
    def _execute_function(self, function_name: str, parameters: Dict) -> Dict:
        """Execute the requested function and return results"""
        try:
            if function_name == "search_products":
                return self._search_products(**parameters)
            elif function_name == "get_shop_stats":
                return self._get_shop_stats(**parameters)
            elif function_name == "get_product_recommendations":
                return self._get_recommendations(**parameters)
            elif function_name == "check_product_availability":
                return self._check_availability(**parameters)
            else:
                return {"error": f"Unknown function: {function_name}"}
                
        except Exception as e:
            logger.error(f"Error executing function {function_name}: {e}")
            return {"error": str(e)}
    
    def _search_products(self, query: str, category: str = None, price_min: float = None, 
                        price_max: float = None, brand: str = None) -> Dict:
        """Search products using existing DatabaseReader"""
        try:
            from .smart_ai_service import DatabaseReader
            
            # Build filters
            filters = {}
            if price_min is not None:
                filters['price_min'] = price_min
            if price_max is not None:
                filters['price_max'] = price_max
            if brand:
                filters['brand'] = brand
            if category:
                filters['category'] = category
            
            # Search products
            db_reader = DatabaseReader()
            products = db_reader.search_products(query, filters)
            
            return {
                "success": True,
                "products": products,
                "count": len(products),
                "query": query,
                "filters": filters
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _get_shop_stats(self, stat_type: str = "overview") -> Dict:
        """Get shop statistics"""
        try:
            from .smart_ai_service import DatabaseReader
            
            db_reader = DatabaseReader()
            stats = db_reader.get_database_stats()
            
            return {
                "success": True,
                "stats": stats,
                "type": stat_type
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _get_recommendations(self, user_preferences: Dict = None, limit: int = 5) -> Dict:
        """Get product recommendations"""
        try:
            from .smart_ai_service import DatabaseReader
            import random
            
            db_reader = DatabaseReader()
            all_products = db_reader.search_products("", {})
            
            # Simple random recommendation for now
            # TODO: Implement smart recommendation based on user_preferences
            recommended = random.sample(all_products, min(limit, len(all_products)))
            
            return {
                "success": True,
                "recommendations": recommended,
                "count": len(recommended),
                "based_on": user_preferences or "general"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _check_availability(self, product_id: int) -> Dict:
        """Check product availability"""
        try:
            from api.models import Product
            
            product = Product.objects.get(id=product_id)
            
            return {
                "success": True,
                "product_id": product_id,
                "name": product.name,
                "available": True,  # Simplified - you can add real inventory check
                "price": float(product.price)
            }
            
        except Product.DoesNotExist:
            return {"success": False, "error": "Product not found"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def generate_response(self, message: str, context: Dict = None, user=None) -> Dict:
        """Generate AI response using old Gemini API with retry logic"""
        if not self.is_available():
            return {
                'success': False,
                'error': 'Gemini service not available',
                'message': None
            }

        # Check cache first
        cache_key = f"gemini_response_{hash(message)}"
        cached_response = cache.get(cache_key)
        if cached_response:
            logger.info("Returning cached Gemini response")
            return cached_response

        max_retries = 3
        for attempt in range(max_retries):
            try:
                start_time = time.time()

                # Prepare context for better responses
                full_message = self._prepare_message_with_context(message, context, user)

                # Check if this is a product search request and handle with function calling
                function_results = []
                if self._should_search_products(message):
                    search_result = self._search_products(message)
                    if search_result.get('success'):
                        function_results.append({
                            'function': 'search_products',
                            'parameters': {'query': message},
                            'result': search_result
                        })

                # Generate response using REST API
                enhanced_prompt = self._create_enhanced_prompt(full_message, function_results)

                url = f"{self.base_url}/models/gemini-1.5-flash:generateContent"
                headers = {
                    'Content-Type': 'application/json',
                }
                data = {
                    'contents': [{
                        'parts': [{'text': enhanced_prompt}]
                    }],
                    'generationConfig': {
                        'maxOutputTokens': self.max_tokens,
                        'temperature': self.temperature
                    }
                }

                response = requests.post(
                    f"{url}?key={self.api_key}",
                    headers=headers,
                    json=data,
                    timeout=30
                )

                response_time = time.time() - start_time

                if response.status_code == 200:
                    response_data = response.json()
                    if 'candidates' in response_data and response_data['candidates']:
                        candidate = response_data['candidates'][0]
                        if 'content' in candidate and 'parts' in candidate['content']:
                            ai_message = candidate['content']['parts'][0].get('text', 'Xin lỗi, tôi không thể trả lời.')
                        else:
                            ai_message = "Xin lỗi, tôi không thể trả lời câu hỏi này."
                    else:
                        ai_message = "Xin lỗi, tôi không thể trả lời câu hỏi này."
                else:
                    logger.error(f"Gemini API error {response.status_code}: {response.text}")
                    ai_message = "Xin lỗi, có lỗi xảy ra khi xử lý yêu cầu."

                result = {
                    'success': True,
                    'message': ai_message,
                    'function_calls': function_results,
                    'response_time': response_time,
                    'model_used': self.model_name,
                    'metadata': {
                        'model': self.model_name,
                        'temperature': self.temperature,
                        'response_length': len(ai_message),
                        'function_calls_count': len(function_results),
                        'attempt': attempt + 1
                    }
                }

                # Cache successful response for 5 minutes
                cache.set(cache_key, result, timeout=300)
                return result

            except Exception as e:
                logger.warning(f"Gemini attempt {attempt + 1} failed: {e}")
                if attempt == max_retries - 1:  # Last attempt
                    logger.error(f"All Gemini attempts failed: {e}")
                    return {
                        'success': False,
                        'error': str(e),
                        'message': None,
                        'function_calls': []
                    }
                time.sleep(1)  # Wait 1 second before retry
    
    def _should_search_products(self, message: str) -> bool:
        """Check if message requires product search"""
        search_keywords = [
            'tìm', 'tìm kiếm', 'có', 'bán', 'shop', 'sản phẩm',
            'áo', 'quần', 'giày', 'dép', 'váy', 'đầm',
            'thun', 'sơ mi', 'jean', 'kaki', 'short'
        ]
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in search_keywords)

    def _create_enhanced_prompt(self, message: str, function_results: List[Dict]) -> str:
        """Create enhanced prompt with function results"""
        prompt_parts = [self.system_instruction, f"\nCâu hỏi: {message}"]

        # Add function results to prompt
        for func_result in function_results:
            if func_result['function'] == 'search_products' and func_result['result'].get('success'):
                products = func_result['result']['products'][:3]  # Top 3 products
                if products:
                    prompt_parts.append(f"\nSản phẩm tìm được:")
                    for i, product in enumerate(products, 1):
                        prompt_parts.append(
                            f"{i}. {product['name']} - {product['price']:,.0f} VND "
                            f"({product['brand']} - {product['category']})"
                        )
                    prompt_parts.append(f"\nTổng cộng tìm thấy {func_result['result']['count']} sản phẩm.")

        prompt_parts.append(f"\nHãy trả lời câu hỏi dựa trên thông tin trên:")
        return "\n".join(prompt_parts)

    def _prepare_message_with_context(self, message: str, context: Dict = None, user=None) -> str:
        """Prepare message with additional context"""
        if not context and not user:
            return message

        context_parts = [f"Câu hỏi của khách hàng: {message}"]

        if user and user.is_authenticated:
            context_parts.append(f"Thông tin khách hàng: {user.get_full_name() or user.username}")

        if context:
            if context.get('conversation_history'):
                history = context['conversation_history'][-2:]  # Last 2 messages
                context_parts.append("Lịch sử hội thoại gần đây:")
                for msg in history:
                    context_parts.append(f"- {msg.get('role', 'user')}: {msg.get('content', '')}")

        return "\n".join(context_parts)


# Global instance
gemini_service = GeminiService()

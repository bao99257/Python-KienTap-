"""
API Documentation for AI Chatbot System
"""

def get_api_documentation():
    """Return comprehensive API documentation"""
    return {
        "title": "AI Chatbot API Documentation",
        "version": "2.0.0",
        "description": "Advanced AI chatbot with Gemini integration and function calling",
        "base_url": "/ai/",
        
        "endpoints": {
            "chat": {
                "url": "/ai/chat/",
                "method": "POST",
                "auth_required": True,
                "description": "Main chat endpoint with AI integration",
                "request_body": {
                    "message": "string (required) - User message",
                    "session_id": "string (optional) - Chat session ID",
                    "context": "object (optional) - Additional context"
                },
                "response": {
                    "message": "string - AI response",
                    "session_id": "string - Session identifier",
                    "suggested_products": "array - Product recommendations",
                    "actions_taken": "array - AI actions performed",
                    "quick_replies": "array - Suggested quick replies",
                    "metadata": "object - Response metadata"
                },
                "example": {
                    "request": {
                        "message": "Tìm áo thun nam size L dưới 500k",
                        "session_id": "uuid-here"
                    },
                    "response": {
                        "message": "Tôi tìm thấy 3 áo thun phù hợp với yêu cầu của bạn...",
                        "suggested_products": [
                            {
                                "id": 1,
                                "name": "Áo thun basic",
                                "price": 450000,
                                "image": "/images/product1.jpg"
                            }
                        ],
                        "actions_taken": [
                            {
                                "type": "product_search",
                                "query": "áo thun nam size L",
                                "results_count": 3
                            }
                        ]
                    }
                }
            },
            
            "test_gemini": {
                "url": "/ai/test-gemini/",
                "method": "GET/POST",
                "auth_required": False,
                "description": "Test Gemini AI integration",
                "response": {
                    "available": "boolean - Service availability",
                    "model": "string - Model name",
                    "api_key_configured": "boolean - API key status"
                }
            },
            
            "status": {
                "url": "/ai/status/",
                "method": "GET",
                "auth_required": False,
                "description": "Get comprehensive AI service status",
                "response": {
                    "services": {
                        "gemini": "object - Gemini service status",
                        "ollama": "object - Ollama service status"
                    },
                    "recommendations": "array - System recommendations"
                }
            },
            
            "conversations": {
                "url": "/ai/conversations/",
                "method": "GET",
                "auth_required": True,
                "description": "Get user conversation history"
            },
            
            "recommendations": {
                "url": "/ai/recommendations/products/",
                "method": "POST",
                "auth_required": True,
                "description": "Get AI product recommendations"
            }
        },
        
        "ai_features": {
            "gemini_integration": {
                "description": "Google Gemini AI for natural conversation",
                "capabilities": [
                    "Natural language understanding",
                    "Context-aware responses",
                    "Function calling for product search",
                    "Vietnamese language support",
                    "Retry logic and caching"
                ],
                "performance": {
                    "response_time": "1-3 seconds",
                    "cache_duration": "5 minutes",
                    "retry_attempts": 3
                }
            },
            
            "function_calling": {
                "description": "AI can automatically call functions based on user intent",
                "available_functions": [
                    "search_products - Search product database",
                    "get_shop_stats - Get shop statistics",
                    "get_recommendations - Get personalized recommendations",
                    "check_availability - Check product availability"
                ]
            },
            
            "fallback_system": {
                "description": "Multi-layer fallback for reliability",
                "layers": [
                    "1. Gemini AI (primary)",
                    "2. Ollama AI (secondary)",
                    "3. Rule-based responses (fallback)"
                ]
            }
        },
        
        "setup_guide": {
            "gemini_setup": {
                "step_1": "Visit https://aistudio.google.com/",
                "step_2": "Login with Google account",
                "step_3": "Click 'Get API key' → 'Create API key'",
                "step_4": "Copy API key to .env file: GEMINI_API_KEY=your_key_here",
                "step_5": "Restart Django server"
            },
            
            "testing": {
                "basic_test": "GET /ai/status/ - Check service status",
                "gemini_test": "GET /ai/test-gemini/ - Test Gemini connection",
                "chat_test": "POST /ai/test-search/ - Test chat functionality"
            }
        },
        
        "error_handling": {
            "common_errors": {
                "API_KEY_INVALID": "Check Gemini API key in .env file",
                "SERVICE_UNAVAILABLE": "Check internet connection and API quotas",
                "TIMEOUT": "Increase timeout settings or check network",
                "QUOTA_EXCEEDED": "Wait for quota reset or upgrade plan"
            },
            
            "error_response_format": {
                "status": "error",
                "error": "Error message",
                "traceback": "Detailed error trace (debug mode only)"
            }
        },
        
        "performance_tips": {
            "caching": "Responses cached for 5 minutes to improve speed",
            "retry_logic": "3 automatic retries for failed requests",
            "fallback": "Automatic fallback to Ollama or rule-based responses",
            "optimization": "Use specific queries for better AI responses"
        }
    }

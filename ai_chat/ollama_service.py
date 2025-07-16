"""
Ollama AI Service for simple chat and emotional responses
"""

import requests
import json
import time
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class OllamaService:
    """Service để giao tiếp với Ollama AI"""
    
    def __init__(self):
        self.base_url = "http://localhost:11434"
        self.model = "llama3.2"
        self.available = None
    
    def is_available(self) -> bool:
        """Kiểm tra Ollama có sẵn không"""
        if self.available is not None:
            return self.available
            
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            self.available = response.status_code == 200
            return self.available
        except Exception as e:
            logger.warning(f"Ollama not available: {e}")
            self.available = False
            return False
    
    def generate_response(self, prompt: str, max_tokens: int = 150) -> Dict:
        """Tạo response từ Ollama"""
        if not self.is_available():
            return {
                'success': False,
                'error': 'Ollama service not available',
                'message': ''
            }
        
        start_time = time.time()
        
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "max_tokens": max_tokens,
                    "top_p": 0.9
                }
            }
            
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                message = result.get('response', '').strip()
                
                # Clean up response
                message = self._clean_response(message)
                
                return {
                    'success': True,
                    'message': message,
                    'model_used': self.model,
                    'response_time': time.time() - start_time
                }
            else:
                logger.error(f"Ollama API error: {response.status_code}")
                return {
                    'success': False,
                    'error': f'API error: {response.status_code}',
                    'message': ''
                }
                
        except requests.exceptions.Timeout:
            logger.error("Ollama request timeout")
            return {
                'success': False,
                'error': 'Request timeout',
                'message': ''
            }
        except Exception as e:
            logger.error(f"Ollama error: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': ''
            }
    
    def _clean_response(self, message: str) -> str:
        """Làm sạch response từ Ollama"""
        if not message:
            return "Xin lỗi, tôi không hiểu câu hỏi của bạn. Bạn có thể nói rõ hơn không?"
        
        # Remove markdown formatting
        message = message.replace('**', '').replace('*', '')
        
        # Remove excessive newlines
        message = '\n'.join(line.strip() for line in message.split('\n') if line.strip())
        
        # Limit length
        if len(message) > 300:
            message = message[:300] + "..."
        
        return message


# Global instance
ollama_service = OllamaService()

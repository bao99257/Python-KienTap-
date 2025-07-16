#!/usr/bin/env python
"""
Test policy features và anti-"..." functionality
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from ai_chat.hybrid_chatbot import hybrid_chatbot

def test_policy_features():
    """Test policy và các tính năng chống "..." """
    
    print("📋 TESTING POLICY & ANTI-... FEATURES")
    print("=" * 50)
    
    test_cases = [
        # Policy questions
        "chính sách tư vấn size",
        "quy định đổi trả",
        "policy của shop",
        
        # Shop info
        "shop ở đâu",
        "thông tin cửa hàng",
        "địa chỉ shop",
        
        # Size guide với policy
        "bảng size chi tiết",
        "hướng dẫn chọn size",
        
        # General questions
        "shop bán gì",
        "có gì hay không",
        "tôi muốn hỏi",
        
        # Edge cases that might cause "..."
        "nếu tôi không chắc chắn về size",
        "muốn được tư vấn thêm",
        "hoặc muốn",
    ]
    
    for i, message in enumerate(test_cases, 1):
        print(f"\n📝 Test {i}: '{message}'")
        print("-" * 40)
        
        try:
            response = hybrid_chatbot.process_message(message)
            
            print(f"✅ Intent: {response.get('intent', 'N/A')}")
            
            # Check for incomplete responses (ending with ...)
            message_text = response.get('message', '')
            if message_text.endswith('...') or '...' in message_text[-20:]:
                print("🚨 WARNING: Response contains '...' - might be incomplete!")
            
            print(f"📄 Message: {message_text[:200]}...")
            print(f"🔘 Quick replies: {response.get('quick_replies', [])}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
        
        print()

if __name__ == "__main__":
    test_policy_features()

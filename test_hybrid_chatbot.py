#!/usr/bin/env python
"""
Test Hybrid Chatbot với bảng size chuẩn
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from ai_chat.hybrid_chatbot import hybrid_chatbot

def test_hybrid_chatbot():
    """Test hybrid chatbot với các scenarios khác nhau"""
    
    print("🤖 TESTING HYBRID CHATBOT")
    print("=" * 50)
    
    test_cases = [
        # Size consultation với measurements
        "tôi 1m56 nặng 59kg mặc size gì",
        "cao 1m65 nặng 56kg size áo",
        "1m70 75kg size quần jean bao nhiêu",
        
        # Size guide requests
        "Bảng size chi tiết",
        "tư vấn size",
        "hướng dẫn chọn size",
        
        # Greetings
        "xin chào",
        "hello",
        
        # Emotional
        "buồn qá",
        "vui quá",
        
        # Product search
        "tìm áo thun",
        "có áo hoodie không",
        
        # General chat
        "hôm nay thế nào",
        "shop ở đâu",
    ]
    
    for i, message in enumerate(test_cases, 1):
        print(f"\n📝 Test {i}: '{message}'")
        print("-" * 40)
        
        try:
            response = hybrid_chatbot.process_message(message)
            
            print(f"✅ Intent: {response.get('intent', 'N/A')}")
            print(f"📄 Message: {response.get('message', '')[:150]}...")
            print(f"🔘 Quick replies: {response.get('quick_replies', [])}")
            
            if 'metadata' in response:
                metadata = response['metadata']
                if 'measurements' in metadata:
                    print(f"📏 Measurements: {metadata['measurements']}")
                if 'recommended_sizes' in metadata:
                    sizes = [s['size'] for s in metadata['recommended_sizes']]
                    print(f"👕 Recommended sizes: {sizes}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
        
        print()

def test_size_extraction():
    """Test size measurement extraction"""
    print("\n🔍 TESTING SIZE EXTRACTION")
    print("=" * 50)
    
    from ai_chat.size_consultant import size_consultant
    
    test_messages = [
        "tôi 1m56 nặng 59kg",
        "cao 165cm cân 56kg",
        "1.65m 56kg",
        "chiều cao 170 cân nặng 65",
        "nam 1m75 80kg",
        "nữ cao 160 nặng 50"
    ]
    
    for message in test_messages:
        measurements = size_consultant.extract_measurements(message)
        product_type = size_consultant.detect_product_type(message + " áo")
        
        print(f"Message: '{message}'")
        print(f"  Measurements: {measurements}")
        print(f"  Product type: {product_type}")
        print()

if __name__ == "__main__":
    test_hybrid_chatbot()
    test_size_extraction()

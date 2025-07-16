#!/usr/bin/env python
"""
Test edge cases cho size consultation
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from ai_chat.hybrid_chatbot import hybrid_chatbot

def test_edge_cases():
    """Test các trường hợp edge case"""
    
    print("🚨 TESTING EDGE CASES")
    print("=" * 50)
    
    edge_cases = [
        # Trường hợp của user
        "tôi cao 1m56 nặng 89kg",
        "cao 1m56 nặng 90kg",
        "1m50 nặng 79kg",   # New case

        # Các trường hợp khác
        "1m50 nặng 100kg",  # Quá nặng
        "2m00 nặng 50kg",   # Quá cao, quá nhẹ
        "1m40 nặng 30kg",   # Quá nhỏ
        "1m52 nặng 75kg",   # Borderline case

        # Trường hợp bình thường để so sánh
        "1m65 nặng 60kg",   # Bình thường
        "1m70 nặng 70kg",   # Bình thường
    ]
    
    for i, message in enumerate(edge_cases, 1):
        print(f"\n📝 Test {i}: '{message}'")
        print("-" * 40)
        
        try:
            response = hybrid_chatbot.process_message(message)
            
            print(f"✅ Intent: {response.get('intent', 'N/A')}")
            print(f"📄 Message: {response.get('message', '')[:200]}...")
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

if __name__ == "__main__":
    test_edge_cases()

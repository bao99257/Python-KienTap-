#!/usr/bin/env python
"""
Test smart AI directly
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from ai_chat.smart_ai_service import smart_ai

def test_smart_ai():
    """Test smart AI directly"""
    
    print("🔍 TESTING SMART AI DIRECTLY")
    print("=" * 50)
    
    test_messages = [
        "tôi 1m56 nặng 59kg mặc size gì",
        "cao 1m65 nặng 56kg size nào phù hợp",
        "Tư vấn size",
        "xin chào"
    ]
    
    for message in test_messages:
        print(f"\n📝 Testing: '{message}'")
        
        try:
            # Test intent detection first
            intent = smart_ai._simple_intent_detection(message.lower())
            print(f"   Intent detected: {intent}")
            
            # Test full processing
            response = smart_ai.process_message(message, user=None, session_id='test123')
            
            print(f"   Response type: {type(response)}")
            print(f"   Response keys: {list(response.keys()) if isinstance(response, dict) else 'Not dict'}")
            
            if isinstance(response, dict):
                print(f"   Intent in response: {response.get('intent')}")
                print(f"   Message: {response.get('message', '')[:100]}...")
                print(f"   Quick replies: {response.get('quick_replies', [])}")
                print(f"   Metadata: {response.get('metadata', {})}")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            import traceback
            traceback.print_exc()
        
        print("-" * 40)

if __name__ == "__main__":
    test_smart_ai()

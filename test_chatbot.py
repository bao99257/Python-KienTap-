#!/usr/bin/env python
"""
Test script for Enhanced Chatbot
"""

import requests
import json
import uuid

def test_chatbot():
    """Test enhanced chatbot functionality"""
    
    base_url = "http://127.0.0.1:8000/ai"
    session_id = str(uuid.uuid4())
    
    test_cases = [
        {
            "name": "Greeting",
            "message": "Xin chào!"
        },
        {
            "name": "Product Search",
            "message": "Tìm áo thun nam size L dưới 500k"
        },
        {
            "name": "Price Inquiry", 
            "message": "Giá áo thun bao nhiêu?"
        },
        {
            "name": "Size Question",
            "message": "Tư vấn size áo cho người cao 1m70"
        },
        {
            "name": "Policy Question",
            "message": "Chính sách đổi trả như thế nào?"
        },
        {
            "name": "General Chat",
            "message": "Hôm nay thời tiết đẹp nhỉ?"
        },
        {
            "name": "Goodbye",
            "message": "Cảm ơn, tạm biệt!"
        }
    ]
    
    print("🤖 TESTING ENHANCED CHATBOT")
    print("=" * 50)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['name']}")
        print(f"👤 User: {test_case['message']}")
        
        try:
            response = requests.post(
                f"{base_url}/test-enhanced/",
                json={
                    "message": test_case['message'],
                    "session_id": session_id
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                ai_response = data.get('ai_response', {})
                
                print(f"🤖 Bot: {ai_response.get('message', 'No response')}")
                
                if ai_response.get('quick_replies'):
                    print(f"💡 Quick replies: {', '.join(ai_response['quick_replies'])}")
                
                if ai_response.get('suggested_products'):
                    products = ai_response['suggested_products']
                    print(f"🛍️ Found {len(products)} products")
                
                print(f"📊 Intent: {ai_response.get('intent', 'unknown')}")
                print(f"⚡ Response time: {ai_response.get('response_time', 0):.2f}s")
                
            else:
                print(f"❌ Error {response.status_code}: {response.text}")
                
        except Exception as e:
            print(f"❌ Exception: {e}")
        
        print("-" * 30)

if __name__ == "__main__":
    test_chatbot()

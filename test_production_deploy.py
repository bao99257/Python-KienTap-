#!/usr/bin/env python3
"""
Test script để kiểm tra Hybrid AI Production Deployment
"""
import requests
import json

def test_hybrid_ai():
    """Test Hybrid AI với các test cases quan trọng"""
    
    base_url = "http://127.0.0.1:8001/ai/test-enhanced/"
    
    test_cases = [
        {
            "name": "Size Consultation - Special Case",
            "message": "cao 1m50 nặng 80kg nên mặc size gì",
            "expected_keywords": ["ngoài bảng size", "liên hệ", "tư vấn"]
        },
        {
            "name": "Size Consultation - Normal Case", 
            "message": "cao 1m65 nặng 60kg nên mặc size gì",
            "expected_keywords": ["Size M", "phù hợp"]
        },
        {
            "name": "Product Search",
            "message": "tìm áo thun nam dưới 500k",
            "expected_keywords": ["áo thun", "sản phẩm", "giá"]
        },
        {
            "name": "General Chat",
            "message": "xin chào bạn",
            "expected_keywords": ["chào", "giúp"]
        }
    ]
    
    print("🚀 TESTING HYBRID AI PRODUCTION DEPLOYMENT")
    print("=" * 60)
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n📋 Test {i}: {test['name']}")
        print(f"💬 Message: {test['message']}")
        
        try:
            response = requests.post(
                base_url,
                json={"message": test['message']},
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                ai_response = data.get('ai_response', {})
                message = ai_response.get('message', '')
                
                print(f"✅ Status: SUCCESS")
                print(f"🤖 AI Response: {message[:100]}...")
                
                # Check keywords
                found_keywords = []
                for keyword in test['expected_keywords']:
                    if keyword.lower() in message.lower():
                        found_keywords.append(keyword)
                
                if found_keywords:
                    print(f"🎯 Keywords Found: {found_keywords}")
                else:
                    print(f"⚠️  Expected Keywords: {test['expected_keywords']}")
                    
            else:
                print(f"❌ Status: FAILED - {response.status_code}")
                print(f"Error: {response.text}")
                
        except Exception as e:
            print(f"❌ Status: ERROR - {str(e)}")
    
    print("\n" + "=" * 60)
    print("🏁 DEPLOYMENT TEST COMPLETED!")

if __name__ == "__main__":
    test_hybrid_ai()

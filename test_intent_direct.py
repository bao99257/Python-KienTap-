#!/usr/bin/env python
"""
Test intent detection trực tiếp
"""

import requests
import json

def test_intent_detection():
    """Test intent detection với các message khác nhau"""
    
    base_url = "http://127.0.0.1:8000/ai/test-search/"
    
    test_cases = [
        {"message": "Xin chào!", "expected_intent": "greeting"},
        {"message": "Giá áo thun bao nhiêu?", "expected_intent": "price_inquiry"},
        {"message": "Tư vấn size áo", "expected_intent": "size_inquiry"},
        {"message": "Chính sách đổi trả", "expected_intent": "policy_question"},
        {"message": "Còn hàng áo thun không?", "expected_intent": "stock_check"},
        {"message": "Gợi ý outfit", "expected_intent": "recommendation"},
        {"message": "Tìm áo thun", "expected_intent": "product_search"},
        {"message": "Cảm ơn, tạm biệt!", "expected_intent": "goodbye"},
    ]
    
    print("🎯 TESTING INTENT DETECTION")
    print("=" * 50)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. Testing: '{test_case['message']}'")
        print(f"   Expected: {test_case['expected_intent']}")
        
        try:
            response = requests.post(
                base_url,
                json={"message": test_case['message']},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                ai_response = data.get('ai_response', {})
                
                # Check both direct and metadata
                detected_intent = ai_response.get('intent') or ai_response.get('metadata', {}).get('intent', 'NOT_FOUND')
                confidence = ai_response.get('confidence') or ai_response.get('metadata', {}).get('confidence', 'NOT_FOUND')
                
                print(f"   Detected: {detected_intent}")
                print(f"   Confidence: {confidence}")
                
                # Check if intent matches
                if detected_intent == test_case['expected_intent']:
                    print("   ✅ CORRECT")
                elif detected_intent == 'NOT_FOUND':
                    print("   ❌ NO INTENT DETECTED")
                else:
                    print(f"   ⚠️ MISMATCH (got {detected_intent})")
                
                # Show response preview
                message_preview = ai_response.get('message', '')[:80]
                print(f"   Response: {message_preview}...")
                
            else:
                print(f"   ❌ HTTP Error: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")
    
    print(f"\n" + "=" * 50)
    print("🔍 DEBUGGING INFO:")
    
    # Test one case in detail
    try:
        response = requests.post(
            base_url,
            json={"message": "Xin chào!"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"Full response structure:")
            print(f"- Status: {data.get('status')}")
            print(f"- AI Response keys: {list(data.get('ai_response', {}).keys())}")
            
            ai_response = data.get('ai_response', {})
            if 'metadata' in ai_response:
                print(f"- Metadata: {ai_response['metadata']}")
            
    except Exception as e:
        print(f"Debug test failed: {e}")

if __name__ == "__main__":
    test_intent_detection()

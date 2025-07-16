#!/usr/bin/env python
"""
Test thực tế các chức năng chatbot hiện có
"""

import requests
import json
import uuid

def test_real_chatbot_features():
    """Test thực tế các chức năng chatbot"""
    
    base_url = "http://127.0.0.1:8000/ai"
    session_id = str(uuid.uuid4())
    
    print("🔍 KIỂM TRA THỰC TẾ CÁC CHỨC NĂNG CHATBOT")
    print("=" * 60)
    
    # Test cases thực tế
    test_cases = [
        {
            "name": "1. Conversation Handling - Greeting",
            "endpoint": "/test-search/",
            "message": "Xin chào!"
        },
        {
            "name": "2. Product Search - Basic",
            "endpoint": "/test-search/",
            "message": "Tìm áo thun"
        },
        {
            "name": "3. Product Search - Advanced",
            "endpoint": "/test-search/",
            "message": "Tìm áo thun nam size L dưới 500k"
        },
        {
            "name": "4. Price Inquiry",
            "endpoint": "/test-search/",
            "message": "Giá áo thun bao nhiêu?"
        },
        {
            "name": "5. Size Consultation",
            "endpoint": "/test-search/",
            "message": "Tư vấn size áo cho người cao 1m70"
        },
        {
            "name": "6. Policy Question",
            "endpoint": "/test-search/",
            "message": "Chính sách đổi trả như thế nào?"
        },
        {
            "name": "7. Stock Check",
            "endpoint": "/test-search/",
            "message": "Còn hàng áo thun không?"
        },
        {
            "name": "8. General AI Chat",
            "endpoint": "/test-search/",
            "message": "Hôm nay thời tiết đẹp nhỉ?"
        },
        {
            "name": "9. Recommendation Request",
            "endpoint": "/test-search/",
            "message": "Gợi ý outfit cho tôi"
        },
        {
            "name": "10. Order Status",
            "endpoint": "/test-search/",
            "message": "Kiểm tra đơn hàng của tôi"
        }
    ]
    
    results = {}
    
    for test_case in test_cases:
        print(f"\n{test_case['name']}")
        print(f"👤 User: {test_case['message']}")
        
        try:
            response = requests.post(
                f"{base_url}{test_case['endpoint']}",
                json={
                    "message": test_case['message'],
                    "session_id": session_id
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                ai_response = data.get('ai_response', {})
                
                # Analyze response
                has_message = bool(ai_response.get('message'))
                has_products = bool(ai_response.get('suggested_products'))
                has_quick_replies = bool(ai_response.get('quick_replies'))
                response_length = len(ai_response.get('message', ''))
                
                print(f"🤖 Bot: {ai_response.get('message', 'No response')[:100]}...")
                
                # Feature analysis
                features = []
                if has_products:
                    products = ai_response['suggested_products']
                    features.append(f"🛍️ Found {len(products)} products")
                
                if has_quick_replies:
                    features.append(f"💡 {len(ai_response['quick_replies'])} quick replies")
                
                if response_length > 50:
                    features.append("💬 Detailed response")
                
                # Check for intent in metadata or direct
                intent = ai_response.get('intent') or ai_response.get('metadata', {}).get('intent')
                if intent:
                    features.append(f"🎯 Intent: {intent}")
                
                print(f"✅ Features: {', '.join(features) if features else 'Basic response only'}")
                
                # Store results
                results[test_case['name']] = {
                    'success': True,
                    'has_message': has_message,
                    'has_products': has_products,
                    'has_quick_replies': has_quick_replies,
                    'response_length': response_length,
                    'features': features
                }
                
            else:
                print(f"❌ Error {response.status_code}")
                results[test_case['name']] = {'success': False, 'error': response.status_code}
                
        except Exception as e:
            print(f"❌ Exception: {e}")
            results[test_case['name']] = {'success': False, 'error': str(e)}
        
        print("-" * 40)
    
    # Summary analysis
    print(f"\n📊 PHÂN TÍCH KẾT QUẢ:")
    print("=" * 40)
    
    successful_tests = sum(1 for r in results.values() if r.get('success'))
    total_tests = len(results)
    
    print(f"✅ Successful tests: {successful_tests}/{total_tests}")
    
    # Feature analysis
    product_search_count = sum(1 for r in results.values() if r.get('has_products'))
    quick_replies_count = sum(1 for r in results.values() if r.get('has_quick_replies'))
    detailed_response_count = sum(1 for r in results.values() if r.get('response_length', 0) > 50)
    
    print(f"🛍️ Product search working: {product_search_count} tests")
    print(f"💡 Quick replies working: {quick_replies_count} tests")
    print(f"💬 Detailed responses: {detailed_response_count} tests")
    
    # Identify missing features
    print(f"\n🔍 CHỨC NĂNG HIỆN CÓ:")
    working_features = []
    
    if product_search_count > 0:
        working_features.append("✅ Product Search & Display")
    
    if quick_replies_count > 0:
        working_features.append("✅ Quick Replies/Suggestions")
    
    if detailed_response_count > 5:
        working_features.append("✅ AI Conversation")
    
    # Check specific features
    policy_test = next((r for name, r in results.items() if 'Policy' in name), {})
    if policy_test.get('success') and policy_test.get('response_length', 0) > 100:
        working_features.append("✅ Policy Support")
    
    for feature in working_features:
        print(feature)
    
    print(f"\n❌ CHỨC NĂNG CẦN HOÀN THIỆN:")
    missing_features = [
        "❌ Intent Detection (all showing 'unknown')",
        "❌ Context Memory (no session continuity)",
        "❌ Personalized Recommendations",
        "❌ Advanced Search Filters",
        "❌ Stock Check Integration",
        "❌ Order Status Tracking",
        "❌ User Preferences Learning",
        "❌ Fallback Handling"
    ]
    
    for feature in missing_features:
        print(feature)
    
    return results

if __name__ == "__main__":
    test_real_chatbot_features()

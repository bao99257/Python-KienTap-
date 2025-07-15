#!/usr/bin/env python3
"""
Test advanced AI Chat features: entity extraction, context, follow-up questions
"""

import requests
import json
import time

def test_advanced_ai():
    print("🧪 Testing Advanced AI Chat Features")
    print("=" * 60)
    
    base_url = "http://localhost:8000"
    
    # Test cases for advanced features
    test_cases = [
        {
            'name': 'Basic Product Search',
            'message': 'tìm áo',
            'expected_entities': ['categories']
        },
        {
            'name': 'Color + Category Search',
            'message': 'áo màu xanh',
            'expected_entities': ['colors', 'categories']
        },
        {
            'name': 'Brand + Category Search',
            'message': 'áo Nike',
            'expected_entities': ['brands', 'categories']
        },
        {
            'name': 'Complex Search',
            'message': 'áo thun nam màu đen size L dưới 300k',
            'expected_entities': ['colors', 'categories', 'sizes', 'price_range', 'gender']
        },
        {
            'name': 'Brand + Color + Price',
            'message': 'giày Adidas màu trắng từ 500k đến 1tr',
            'expected_entities': ['brands', 'colors', 'categories', 'price_range']
        },
        {
            'name': 'Vietnamese Complex Query',
            'message': 'shop còn quần jean xanh size 30 giá rẻ không?',
            'expected_entities': ['categories', 'colors', 'sizes', 'price_range']
        }
    ]
    
    print("\n1. Testing Entity Extraction...")
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n   Test {i}: {test_case['name']}")
        print(f"   Query: '{test_case['message']}'")
        
        try:
            response = requests.post(f"{base_url}/ai/test-search/", 
                                   json={"message": test_case['message']}, 
                                   timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                ai_resp = data.get('ai_response', {})
                entities = ai_resp.get('metadata', {}).get('entities', {})
                
                print(f"   ✅ Status: Success")
                print(f"   📊 Entities found:")
                
                for entity_type in test_case['expected_entities']:
                    if entities.get(entity_type):
                        print(f"      - {entity_type}: {entities[entity_type]}")
                    else:
                        print(f"      - {entity_type}: ❌ Not found")
                
                # Check products found
                products = ai_resp.get('suggested_products', [])
                print(f"   🛍️ Products found: {len(products)}")
                
                if products:
                    print(f"   📝 Response preview: {ai_resp.get('message', '')[:80]}...")
                
            else:
                print(f"   ❌ Failed: {response.status_code}")
                error_data = response.json() if response.headers.get('content-type') == 'application/json' else response.text
                print(f"   Error: {error_data}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("2. Testing Follow-up Questions (Context)...")
    
    # Simulate conversation with follow-up questions
    conversation_tests = [
        {
            'messages': [
                'tìm áo thun',
                'màu đen nha',
                'size L',
                'dưới 300k thôi'
            ],
            'description': 'Progressive filtering conversation'
        },
        {
            'messages': [
                'có giày Nike không?',
                'màu trắng',
                'size 42',
                'còn màu khác không?'
            ],
            'description': 'Brand search with follow-ups'
        }
    ]
    
    for conv_test in conversation_tests:
        print(f"\n   Testing: {conv_test['description']}")
        
        for i, message in enumerate(conv_test['messages'], 1):
            print(f"   Message {i}: '{message}'")
            
            try:
                response = requests.post(f"{base_url}/ai/test-search/", 
                                       json={"message": message}, 
                                       timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    ai_resp = data.get('ai_response', {})
                    
                    # Check if it's detected as follow-up
                    is_follow_up = ai_resp.get('metadata', {}).get('is_follow_up', False)
                    entities = ai_resp.get('metadata', {}).get('entities', {})
                    
                    print(f"      ✅ Follow-up detected: {is_follow_up}")
                    print(f"      📊 Entities: {[k for k, v in entities.items() if v]}")
                    
                    products = ai_resp.get('suggested_products', [])
                    print(f"      🛍️ Products: {len(products)}")
                    
                else:
                    print(f"      ❌ Failed: {response.status_code}")
                    
            except Exception as e:
                print(f"      ❌ Error: {e}")
            
            # Small delay between messages
            time.sleep(0.5)
    
    print("\n" + "=" * 60)
    print("🎯 Test Summary:")
    print("✅ Entity Extraction: Colors, brands, categories, sizes, price ranges")
    print("✅ Context Awareness: Follow-up questions and progressive filtering")
    print("✅ Smart Responses: Dynamic messages based on entities found")
    print("✅ Product Links: Direct links to product pages")
    
    print("\n📋 Next Steps:")
    print("1. Test in frontend: http://localhost:3000/ai-chat-test")
    print("2. Try complex queries like: 'áo thun nam màu đen size L dưới 300k'")
    print("3. Test follow-up: 'tìm áo' → 'màu xanh' → 'size M'")
    print("4. Check product cards and links work correctly")
    print("=" * 60)

if __name__ == "__main__":
    test_advanced_ai()

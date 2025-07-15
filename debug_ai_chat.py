#!/usr/bin/env python3
"""
Debug script for AI Chat 500 error
"""

import requests
import json

def debug_ai_chat():
    print("🔧 Debugging AI Chat 500 Error...")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    # Test 1: Basic connection
    print("\n1. Testing basic connection...")
    try:
        response = requests.get(f"{base_url}/ai/test/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ Basic connection working")
            print(f"   Response: {data}")
        else:
            print(f"❌ Basic connection failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to backend: {e}")
        return False
    
    # Test 2: Test product search (no auth)
    print("\n2. Testing product search (no auth)...")
    try:
        test_data = {"message": "tìm áo màu xanh"}
        response = requests.post(f"{base_url}/ai/test-search/", json=test_data, timeout=10)

        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print("✅ Product search working!")
            print(f"   Status: {data.get('status', 'N/A')}")

            if 'ai_response' in data:
                ai_resp = data['ai_response']
                if isinstance(ai_resp, dict) and 'message' in ai_resp:
                    print(f"   AI Message: {ai_resp['message'][:100]}...")
                    if 'suggested_products' in ai_resp:
                        products = ai_resp['suggested_products']
                        print(f"   Found {len(products)} products")
                else:
                    print(f"   AI Response: {ai_resp}")
        else:
            error_text = response.text
            print(f"❌ Product search failed: {response.status_code}")
            print(f"   Error: {error_text}")

            # Try to parse JSON error
            try:
                error_data = response.json()
                if 'traceback' in error_data:
                    print(f"   Traceback: {error_data['traceback']}")
            except:
                pass

    except Exception as e:
        print(f"❌ Product search error: {e}")

    # Test 3: Debug endpoint
    print("\n3. Testing debug endpoint...")
    try:
        test_data = {"message": "debug test"}
        response = requests.post(f"{base_url}/ai/debug/", json=test_data, timeout=10)

        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print("✅ Debug endpoint working")
            print(f"   Import Status: {data.get('import_status', 'N/A')}")
            print(f"   AI Status: {data.get('ai_status', 'N/A')}")
        else:
            error_text = response.text
            print(f"❌ Debug endpoint failed: {response.status_code}")
            print(f"   Error: {error_text}")

    except Exception as e:
        print(f"❌ Debug endpoint error: {e}")
    
    # Test 4: Check Django logs
    print("\n4. Django Server Logs:")
    print("   Check your Django terminal for detailed error messages")
    print("   Look for Python tracebacks and import errors")

    # Test 5: Manual product check
    print("\n5. Manual Product Model Check:")
    print("   Run this in Django shell:")
    print("   python manage.py shell")
    print("   >>> from api.models import Product")
    print("   >>> Product.objects.count()")
    
    print("\n" + "=" * 50)
    print("🎯 Next Steps:")
    print("1. Check Django server logs for detailed errors")
    print("2. Run: python manage.py shell")
    print("3. Test: from api.models import Product")
    print("4. If Product import fails, check INSTALLED_APPS")
    print("5. If database error, run: python manage.py migrate")
    print("=" * 50)

def test_simple_message():
    """Test with simple message that shouldn't trigger product search"""
    print("\n🧪 Testing simple message...")
    
    try:
        response = requests.post('http://localhost:8000/ai/chat/', 
                               json={"message": "xin chào"}, 
                               timeout=5)
        
        print(f"Simple message status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Simple message works")
            print(f"   Response: {data.get('message', 'No message')[:100]}...")
        else:
            print(f"❌ Simple message failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Simple message error: {e}")

if __name__ == "__main__":
    debug_ai_chat()
    test_simple_message()

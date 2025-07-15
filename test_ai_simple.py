#!/usr/bin/env python3
"""
Simple AI Chat test - no authentication required
"""

import requests
import json

def test_ai_simple():
    print("🧪 Simple AI Chat Test (No Auth Required)")
    print("=" * 50)

    base_url = "http://localhost:8000"

    # Test 1: Basic test endpoint
    print("\n1. Testing basic endpoint...")
    try:
        response = requests.get(f"{base_url}/ai/test/", timeout=5)
        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print("✅ Basic endpoint working")
            print(f"   Message: {data.get('message', 'N/A')}")
            print(f"   Import Status: {data.get('import_status', 'N/A')}")
        else:
            print(f"❌ Basic endpoint failed: {response.text}")

    except Exception as e:
        print(f"❌ Cannot connect to backend: {e}")
        print("\n💡 Make sure Django server is running:")
        print("   python manage.py runserver")
        return False

    # Test 2: Product search test
    print("\n2. Testing product search...")
    test_messages = [
        "xin chào",
        "tìm áo",
        "tìm áo màu xanh",
        "giày dưới 500k",
        "áo Nike màu đen",
        "quần jean size 30",
        "sản phẩm giá rẻ"
    ]

    for message in test_messages:
        try:
            print(f"\n   Testing: '{message}'")
            response = requests.post(f"{base_url}/ai/test-search/",
                                   json={"message": message},
                                   timeout=10)

            print(f"   Status: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                ai_resp = data.get('ai_response', {})

                if isinstance(ai_resp, dict):
                    msg = ai_resp.get('message', 'No message')
                    products = ai_resp.get('suggested_products', [])
                    print(f"   ✅ Response: {msg[:60]}...")
                    print(f"   ✅ Products found: {len(products)}")
                else:
                    print(f"   ⚠️ Unexpected response: {ai_resp}")

            else:
                error_data = response.json() if response.headers.get('content-type') == 'application/json' else response.text
                print(f"   ❌ Failed: {error_data}")

                # Show traceback if available
                if isinstance(error_data, dict) and 'traceback' in error_data:
                    print(f"   📋 Error details:")
                    print(f"      {error_data.get('error', 'Unknown error')}")

        except Exception as e:
            print(f"   ❌ Error: {e}")

    print("\n" + "=" * 50)
    print("🎯 Results Summary:")
    print("✅ If all tests pass: AI Chat is working!")
    print("❌ If tests fail: Check Django logs for details")
    print("\n📋 Next steps:")
    print("1. If working: Test in frontend at http://localhost:3000/ai-chat-test")
    print("2. If failing: Check Django server logs")
    print("3. Common issues: Missing Product model, database not migrated")
    print("=" * 50)

if __name__ == "__main__":
    test_ai_simple()

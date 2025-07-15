#!/usr/bin/env python3
"""
Simple backend test for AI Chat
"""

import requests
import json

def test_backend():
    print("🧪 Testing AI Chat Backend...")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    # Test 1: Basic connection
    print("\n1. Testing basic connection...")
    try:
        response = requests.get(f"{base_url}/api/", timeout=5)
        if response.status_code in [200, 404]:
            print("✅ Backend server is running")
        else:
            print(f"⚠️ Backend returned status: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend. Make sure Django server is running:")
        print("   python manage.py runserver")
        return False
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False
    
    # Test 2: AI test endpoint
    print("\n2. Testing AI test endpoint...")
    try:
        response = requests.get(f"{base_url}/ai/test/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ AI test endpoint working")
            print(f"   Response: {data}")
        else:
            print(f"❌ AI test endpoint failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ AI test endpoint error: {e}")
    
    # Test 3: AI chat without auth (should fail with 401)
    print("\n3. Testing AI chat without authentication...")
    try:
        test_data = {"message": "test"}
        response = requests.post(f"{base_url}/ai/chat/", json=test_data, timeout=5)
        if response.status_code == 401:
            print("✅ AI chat correctly requires authentication")
        elif response.status_code == 403:
            print("✅ AI chat correctly requires authentication (403)")
        else:
            print(f"⚠️ Unexpected status: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ AI chat test error: {e}")
    
    # Test 4: Try to get auth token (optional)
    print("\n4. Testing authentication (optional)...")
    print("   To test with authentication, you need to:")
    print("   1. Create a superuser: python manage.py createsuperuser")
    print("   2. Login via frontend or API")
    print("   3. Use the auth token for AI chat requests")
    
    print("\n" + "=" * 50)
    print("🎯 Next Steps:")
    print("1. If backend tests pass, the issue might be in frontend")
    print("2. Go to: http://localhost:3000/ai-chat-test")
    print("3. Login first, then test AI chat")
    print("4. Check browser console for detailed errors")
    print("=" * 50)
    
    return True

if __name__ == "__main__":
    test_backend()

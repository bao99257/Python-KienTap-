#!/usr/bin/env python3
"""
Test script để kiểm tra AI Chat endpoint
"""

import requests
import json

def test_ai_chat():
    base_url = "http://localhost:8000"
    
    print("🧪 Testing AI Chat endpoints...")
    
    # Test 1: Check if AI test endpoint works
    print("\n1. Testing AI test endpoint...")
    try:
        response = requests.get(f"{base_url}/ai/test/")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {response.json()}")
            print("✅ AI test endpoint is working!")
        else:
            print(f"❌ AI test endpoint failed: {response.text}")
    except Exception as e:
        print(f"❌ Error connecting to AI test endpoint: {e}")
    
    # Test 2: Check if main API is accessible
    print("\n2. Testing main API...")
    try:
        response = requests.get(f"{base_url}/api/")
        print(f"API Status: {response.status_code}")
        if response.status_code in [200, 404]:  # 404 is ok, means server is running
            print("✅ Backend server is running!")
        else:
            print(f"❌ Backend server issue: {response.text}")
    except Exception as e:
        print(f"❌ Error connecting to backend: {e}")
    
    # Test 3: Try to get auth token (if you have test user)
    print("\n3. Testing authentication...")
    try:
        # You can replace with your test credentials
        auth_data = {
            "username": "admin",  # Replace with your admin username
            "password": "admin123"  # Replace with your admin password
        }
        
        response = requests.post(f"{base_url}/auth/jwt/create/", json=auth_data)
        print(f"Auth Status: {response.status_code}")
        
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data.get('access')
            print("✅ Authentication successful!")
            
            # Test 4: Try AI chat with token
            print("\n4. Testing AI chat with authentication...")
            headers = {
                'Authorization': f'JWT {access_token}',
                'Content-Type': 'application/json'
            }
            
            chat_data = {
                "message": "Xin chào",
                "context": {}
            }
            
            response = requests.post(f"{base_url}/ai/chat/", 
                                   json=chat_data, 
                                   headers=headers)
            print(f"AI Chat Status: {response.status_code}")
            
            if response.status_code == 200:
                chat_response = response.json()
                print(f"AI Response: {chat_response.get('message', 'No message')}")
                print("✅ AI Chat is working!")
            else:
                print(f"❌ AI Chat failed: {response.text}")
                
        else:
            print(f"❌ Authentication failed: {response.text}")
            print("💡 Make sure you have created a superuser with: python manage.py createsuperuser")
            
    except Exception as e:
        print(f"❌ Error testing authentication: {e}")
    
    print("\n" + "="*50)
    print("🔧 Troubleshooting tips:")
    print("1. Make sure Django server is running: python manage.py runserver")
    print("2. Check if ai_chat app is in INSTALLED_APPS")
    print("3. Run migrations: python manage.py migrate")
    print("4. Create superuser: python manage.py createsuperuser")
    print("5. Setup AI knowledge: python manage.py setup_ai_knowledge")
    print("="*50)

if __name__ == "__main__":
    test_ai_chat()

#!/usr/bin/env python3
"""
Quick fix script for AI Chat 400 error
"""

import os
import sys

def main():
    print("🔧 Quick Fix for AI Chat 400 Error")
    print("=" * 50)
    
    print("\n📋 Checklist:")
    
    # Check 1: Django server
    print("\n1. ✅ Make sure Django server is running:")
    print("   python manage.py runserver")
    print("   Should see: Starting development server at http://127.0.0.1:8000/")
    
    # Check 2: Migrations
    print("\n2. ✅ Run migrations:")
    print("   python manage.py makemigrations ai_chat")
    print("   python manage.py migrate")
    
    # Check 3: Test AI Chat
    print("\n3. ✅ Test AI Chat:")
    print("   python manage.py test_ai_chat")
    
    # Check 4: Authentication
    print("\n4. ✅ Make sure you're logged in:")
    print("   - Go to http://localhost:3000/login")
    print("   - Login with your credentials")
    print("   - Check browser localStorage for 'authTokens'")
    
    # Check 5: Test endpoint
    print("\n5. ✅ Test AI endpoint manually:")
    print("   python test_ai_simple.py")
    
    # Check 6: Frontend test
    print("\n6. ✅ Test in frontend:")
    print("   - Go to http://localhost:3000/ai-chat-test")
    print("   - Click 'Run Diagnostic Tests'")
    print("   - All tests should pass")
    
    print("\n🚀 Quick Commands:")
    print("   # Setup everything")
    print("   python setup_ai_chat.py")
    print("")
    print("   # Test backend")
    print("   python manage.py test_ai_chat")
    print("")
    print("   # Test endpoint")
    print("   python test_ai_simple.py")
    print("")
    print("   # Start servers")
    print("   python manage.py runserver  # Terminal 1")
    print("   cd frontend && npm start    # Terminal 2")
    
    print("\n🔍 Common Issues:")
    print("   ❌ 'session_id may not be null' -> Fixed in latest code")
    print("   ❌ 'No module named django' -> pip install -r requirements.txt")
    print("   ❌ 'ai_chat not found' -> Add 'ai_chat' to INSTALLED_APPS")
    print("   ❌ 'Authentication failed' -> Login first")
    print("   ❌ 'CORS error' -> Check django-cors-headers")
    
    print("\n💡 Debug Tips:")
    print("   - Check browser console for errors")
    print("   - Check Django server logs")
    print("   - Use AI Chat Test Page for debugging")
    print("   - Verify auth token in localStorage")
    
    print("\n" + "=" * 50)
    print("🎯 Expected Result:")
    print("   AI chatbox should respond with: 'Xin chào! Tôi là trợ lý AI...'")
    print("=" * 50)

if __name__ == "__main__":
    main()

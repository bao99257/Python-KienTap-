#!/usr/bin/env python3
"""
Quick fix for AI Chat 500 error
"""

import os
import sys

def main():
    print("🔧 Quick Fix for AI Chat 500 Error")
    print("=" * 50)
    
    print("\n📋 Step-by-step fix:")
    
    print("\n1. ✅ Check Django server is running:")
    print("   python manage.py runserver")
    print("   Should see: Starting development server at http://127.0.0.1:8000/")
    
    print("\n2. ✅ Test debug endpoint:")
    print("   python debug_ai_chat.py")
    print("   This will show exactly what's causing the 500 error")
    
    print("\n3. ✅ Test in browser:")
    print("   Go to: http://localhost:3000/ai-chat-test")
    print("   Click '🔧 Debug AI' button")
    print("   Check the detailed response")
    
    print("\n4. ✅ Common fixes:")
    print("   # If Product model import fails:")
    print("   python manage.py migrate")
    print("   python manage.py migrate api")
    print("")
    print("   # If database connection fails:")
    print("   python manage.py dbshell")
    print("")
    print("   # If ai_chat app not found:")
    print("   # Add 'ai_chat' to INSTALLED_APPS in backend/settings.py")
    
    print("\n5. ✅ Test simple message first:")
    print("   Try: 'xin chào' (should work)")
    print("   Then: 'tìm áo' (might fail)")
    
    print("\n6. ✅ Check Django logs:")
    print("   Look at Django terminal for Python tracebacks")
    print("   Common errors:")
    print("   - ImportError: No module named 'api'")
    print("   - OperationalError: no such table")
    print("   - AttributeError: module has no attribute")
    
    print("\n🚀 Quick Commands:")
    print("   # Debug the error")
    print("   python debug_ai_chat.py")
    print("")
    print("   # Test in Django shell")
    print("   python manage.py shell")
    print("   >>> from api.models import Product")
    print("   >>> Product.objects.count()")
    print("")
    print("   # Reset if needed")
    print("   python manage.py migrate")
    print("   python manage.py collectstatic --noinput")
    
    print("\n💡 Expected Results:")
    print("   ✅ Debug endpoint shows: '✅ Product model imported'")
    print("   ✅ Debug endpoint shows: '✅ AI response generated'")
    print("   ✅ Simple messages work: 'xin chào'")
    print("   ✅ Product search works: 'tìm áo'")
    
    print("\n" + "=" * 50)
    print("🎯 If still failing:")
    print("1. Share Django server logs (Python tracebacks)")
    print("2. Share debug endpoint response")
    print("3. Check if api app is properly installed")
    print("4. Verify database has Product table")
    print("=" * 50)

if __name__ == "__main__":
    main()

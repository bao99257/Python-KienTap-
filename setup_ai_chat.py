#!/usr/bin/env python3
"""
Setup script for AI Chat - Run this to setup AI Chat functionality
"""

import os
import sys
import django
from django.core.management import execute_from_command_line

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

# Setup Django
django.setup()

def setup_ai_chat():
    print("🤖 Setting up AI Chat...")
    
    # Check if ai_chat is in INSTALLED_APPS
    from django.conf import settings
    if 'ai_chat' not in settings.INSTALLED_APPS:
        print("❌ ai_chat app is not in INSTALLED_APPS!")
        print("Please add 'ai_chat' to INSTALLED_APPS in backend/settings.py")
        return False
    
    print("✅ ai_chat app is in INSTALLED_APPS")
    
    # Run migrations
    print("📊 Running migrations...")
    try:
        execute_from_command_line(['manage.py', 'makemigrations', 'ai_chat'])
        execute_from_command_line(['manage.py', 'migrate'])
        print("✅ Migrations completed")
    except Exception as e:
        print(f"❌ Migration error: {e}")
        return False
    
    # Setup knowledge base
    print("🧠 Setting up AI knowledge base...")
    try:
        from ai_chat.models import AIKnowledgeBase
        
        # Check if knowledge base already exists
        if AIKnowledgeBase.objects.exists():
            print("✅ Knowledge base already exists")
        else:
            execute_from_command_line(['manage.py', 'setup_ai_knowledge'])
            print("✅ Knowledge base created")
    except Exception as e:
        print(f"❌ Knowledge base setup error: {e}")
        return False
    
    # Test AI service
    print("🔧 Testing AI service...")
    try:
        from ai_chat.ai_service import AIResponseGenerator
        
        test_response = AIResponseGenerator.generate_response("xin chào")
        if test_response and test_response.get('message'):
            print("✅ AI service is working")
        else:
            print("⚠️ AI service may have issues")
    except Exception as e:
        print(f"❌ AI service error: {e}")
        return False
    
    print("\n🎉 AI Chat setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Start Django server: python manage.py runserver")
    print("2. Start React frontend: cd frontend && npm start")
    print("3. Visit: http://localhost:3000/ai-chat-test to test")
    print("4. Login and try the AI chatbox!")
    
    return True

if __name__ == "__main__":
    setup_ai_chat()

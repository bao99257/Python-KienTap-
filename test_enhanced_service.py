#!/usr/bin/env python
"""
Test enhanced AI service
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

def test_enhanced_service():
    """Test enhanced AI service"""
    
    print("🔍 TESTING ENHANCED AI SERVICE")
    print("=" * 50)
    
    try:
        from ai_chat.enhanced_ai_service import enhanced_ai_service
        print("✅ Enhanced AI service imported successfully")
        
        # Test generate_response
        message = "Xin chào!"
        context = {'session_id': 'test123'}
        
        print(f"Testing message: '{message}'")
        print(f"Context: {context}")
        
        response = enhanced_ai_service.generate_response(message, user=None, context=context)
        
        print(f"\nResponse type: {type(response)}")
        print(f"Response keys: {list(response.keys()) if isinstance(response, dict) else 'Not a dict'}")
        
        if isinstance(response, dict):
            print(f"\nResponse structure:")
            for key, value in response.items():
                if isinstance(value, str):
                    print(f"  {key}: '{value[:50]}...' (string)")
                elif isinstance(value, list):
                    print(f"  {key}: [{len(value)} items] (list)")
                elif isinstance(value, dict):
                    print(f"  {key}: {list(value.keys())} (dict)")
                else:
                    print(f"  {key}: {value} ({type(value).__name__})")
            
            # Check specific fields
            print(f"\nSpecific checks:")
            print(f"  session_id: {response.get('session_id')}")
            print(f"  intent: {response.get('intent')}")
            print(f"  metadata: {response.get('metadata')}")
            print(f"  message preview: {response.get('message', '')[:100]}")
        
    except ImportError as e:
        print(f"❌ Enhanced AI service import failed: {e}")
    except Exception as e:
        print(f"❌ Enhanced AI service error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_enhanced_service()

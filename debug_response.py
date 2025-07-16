#!/usr/bin/env python
"""
Debug response structure
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from ai_chat.smart_ai_service import smart_ai

def debug_response():
    """Debug response structure"""
    
    print("🔍 DEBUGGING RESPONSE STRUCTURE")
    print("=" * 50)
    
    # Test direct call to smart_ai
    message = "Xin chào!"
    session_id = "test123"
    
    print(f"Input: message='{message}', session_id='{session_id}'")
    
    try:
        # Test intent detection first
        detected_intent = smart_ai._simple_intent_detection(message.lower())
        print(f"Detected intent: {detected_intent}")

        response = smart_ai.process_message(message, user=None, session_id=session_id)

        print(f"\nDirect response type: {type(response)}")
        print(f"Direct response keys: {list(response.keys()) if isinstance(response, dict) else 'Not a dict'}")

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
            print(f"  context: {response.get('context')}")
            print(f"  intent: {response.get('intent')}")
            print(f"  metadata: {response.get('metadata')}")

            # Check if response came from correct handler
            message_content = response.get('message', '')
            if 'AI assistant của shop' in message_content:
                print(f"\n⚠️ Response came from _handle_general_chat (old logic)")
            elif 'Chào mừng đến với shop thời trang' in message_content:
                print(f"\n✅ Response came from _handle_greeting (new logic)")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_response()

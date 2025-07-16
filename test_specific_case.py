#!/usr/bin/env python
"""
Test specific case: 1m50, 79kg
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from ai_chat.hybrid_chatbot import hybrid_chatbot

def test_specific_case():
    """Test case 1m50, 79kg"""
    
    print("🧪 TESTING SPECIFIC CASE: 1m50, 79kg")
    print("=" * 50)
    
    message = "1m50 nặng 79kg"
    
    try:
        response = hybrid_chatbot.process_message(message)
        
        print(f"✅ Intent: {response.get('intent', 'N/A')}")
        print(f"📄 Message:")
        print(response.get('message', ''))
        print(f"🔘 Quick replies: {response.get('quick_replies', [])}")
        
        if 'metadata' in response:
            metadata = response['metadata']
            if 'measurements' in metadata:
                print(f"📏 Measurements: {metadata['measurements']}")
            if 'recommended_sizes' in metadata:
                sizes = [s['size'] for s in metadata['recommended_sizes']]
                print(f"👕 Recommended sizes: {sizes}")
        
        # Check if it's correctly identified as special case
        if response.get('intent') == 'size_consultation_special_case':
            print("✅ CORRECT: Identified as special case")
        elif response.get('intent') == 'size_consultation_success':
            print("❌ WRONG: Should be special case, not success")
        else:
            print(f"❓ UNEXPECTED: Intent is {response.get('intent')}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_specific_case()

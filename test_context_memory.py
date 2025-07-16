#!/usr/bin/env python
"""
Test context memory functionality
"""

import requests
import json
import uuid

def test_context_memory():
    """Test context memory với conversation flow"""
    
    base_url = "http://127.0.0.1:8000/ai/test-search/"
    session_id = str(uuid.uuid4())
    
    print("🧠 TESTING CONTEXT MEMORY")
    print("=" * 50)
    print(f"Session ID: {session_id}")
    
    # Conversation flow
    conversation = [
        {
            "message": "Xin chào!",
            "expected": "greeting response"
        },
        {
            "message": "Tôi muốn tìm áo thun",
            "expected": "product search"
        },
        {
            "message": "Size L",
            "expected": "should remember previous search"
        },
        {
            "message": "Dưới 500k",
            "expected": "should apply price filter to previous search"
        },
        {
            "message": "Cảm ơn!",
            "expected": "goodbye with context"
        }
    ]
    
    for i, turn in enumerate(conversation, 1):
        print(f"\n{i}. User: {turn['message']}")
        print(f"   Expected: {turn['expected']}")
        
        try:
            response = requests.post(
                base_url,
                json={
                    "message": turn['message'],
                    "session_id": session_id
                },
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                ai_response = data.get('ai_response', {})
                
                # Extract key info
                intent = ai_response.get('intent') or ai_response.get('metadata', {}).get('intent', 'unknown')
                message_preview = ai_response.get('message', '')[:100]
                context_info = ai_response.get('context', {})
                
                print(f"   Bot: {message_preview}...")
                print(f"   Intent: {intent}")
                
                if context_info:
                    print(f"   Context: {context_info.get('conversation_turns', 0)} turns")
                
                # Check for products
                products = ai_response.get('suggested_products', [])
                if products:
                    print(f"   Products: {len(products)} found")
                
                # Check for session continuity
                returned_session = ai_response.get('session_id')
                if returned_session == session_id:
                    print("   ✅ Session continuity maintained")
                else:
                    print(f"   ❌ Session mismatch: {returned_session}")
                
            else:
                print(f"   ❌ HTTP Error: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")
        
        print("-" * 30)
    
    print(f"\n📊 CONTEXT MEMORY ANALYSIS:")
    print("=" * 40)
    
    # Test session retrieval
    try:
        # Make one more request to see if context is maintained
        response = requests.post(
            base_url,
            json={
                "message": "Nhắc lại tôi đã tìm gì?",
                "session_id": session_id
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            ai_response = data.get('ai_response', {})
            context_info = ai_response.get('context', {})
            
            print(f"✅ Final context check:")
            print(f"   - Conversation turns: {context_info.get('conversation_turns', 0)}")
            print(f"   - Session active: {context_info.get('session_duration', 'unknown')}")
            print(f"   - Response: {ai_response.get('message', '')[:150]}...")
            
            if context_info.get('conversation_turns', 0) > 0:
                print("✅ Context memory is working!")
            else:
                print("❌ Context memory not working")
        
    except Exception as e:
        print(f"❌ Context test failed: {e}")

if __name__ == "__main__":
    test_context_memory()

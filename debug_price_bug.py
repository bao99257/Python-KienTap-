#!/usr/bin/env python
"""
Debug Price Bug
"""
import os
import sys
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth.models import User
from chatbot.services import SmartChatbotService

def debug_price_bug():
    """Debug the price bug"""
    print("🐛 Debugging Price Bug...")
    
    user, created = User.objects.get_or_create(
        username='debug_user',
        defaults={'email': 'debug@test.com'}
    )
    
    service = SmartChatbotService(user)
    
    message = "có đồ nào dưới 100k không"
    print(f"\n💬 Testing: '{message}'")
    
    # Step 1: Test intent
    print("\n1️⃣ Testing Intent Detection:")
    intent = service.analyze_message(message)
    print(f"   Intent: {intent}")
    
    # Step 2: Test price function directly
    print("\n2️⃣ Testing Price Function Directly:")
    price_result = service.search_products_by_price(message)
    print(f"   Result type: {price_result['type']}")
    print(f"   Message: {price_result['message'][:100]}...")
    
    # Step 3: Test full process
    print("\n3️⃣ Testing Full Process:")
    full_result = service.process_message(message)
    print(f"   Result type: {full_result['type']}")
    print(f"   Message: {full_result['message'][:100]}...")
    
    if full_result['type'] == 'product_list':
        print(f"   ❌ BUG FOUND: Should be no_products!")
        print(f"   Products: {full_result['count']}")
        for product in full_result['products']:
            print(f"     - {product['name']}: {product['price']}đ")
    elif full_result['type'] == 'no_products':
        print(f"   ✅ CORRECT: No products found")
    
    # Step 4: Check if there's a difference
    print("\n4️⃣ Comparison:")
    if price_result['type'] != full_result['type']:
        print(f"   ❌ MISMATCH!")
        print(f"   Price function: {price_result['type']}")
        print(f"   Full process: {full_result['type']}")
        print(f"   → This indicates a routing bug!")
    else:
        print(f"   ✅ MATCH: Both return {price_result['type']}")

def test_other_price_queries():
    """Test other price queries"""
    print("\n\n🧪 Testing Other Price Queries...")
    
    user = User.objects.first()
    service = SmartChatbotService(user)
    
    test_cases = [
        "trên 1 triệu",
        "từ 1 triệu đến 6 triệu", 
        "dưới 2 triệu",
        "tìm áo dưới 100k"
    ]
    
    for i, message in enumerate(test_cases, 1):
        print(f"\n{i}. Testing: '{message}'")
        
        intent = service.analyze_message(message)
        result = service.process_message(message)
        
        print(f"   Intent: {intent['intent']}")
        print(f"   Result: {result['type']}")
        
        if result['type'] == 'product_list':
            print(f"   Products: {result['count']}")
        elif result['type'] == 'no_products':
            print(f"   No products (correct)")

def main():
    """Main function"""
    print("🎯 Starting Price Bug Debug...")
    
    debug_price_bug()
    test_other_price_queries()
    
    print("\n✅ Debug finished!")

if __name__ == "__main__":
    main()

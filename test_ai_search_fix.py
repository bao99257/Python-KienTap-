#!/usr/bin/env python3
"""
Test script để kiểm tra AI chatbox search functionality
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

def test_ai_search():
    """Test AI search functionality"""
    print("🧪 Testing AI Search Functionality")
    print("=" * 50)
    
    try:
        from ai_chat.smart_ai_service import smart_ai
        from api.models import Product, Category, Brand
        
        # Test cases
        test_cases = [
            "tìm áo",
            "tìm quần", 
            "áo",
            "quần",
            "có áo không",
            "shop có bán quần gì",
            "sản phẩm áo"
        ]
        
        print(f"📊 Database Info:")
        print(f"   - Products: {Product.objects.count()}")
        print(f"   - Categories: {Category.objects.count()}")
        print(f"   - Brands: {Brand.objects.count()}")
        print()
        
        # Show sample products
        print("📦 Sample Products:")
        for prod in Product.objects.all()[:5]:
            print(f"   - {prod.name} (Category: {prod.category.title})")
        print()
        
        # Test each case
        for i, query in enumerate(test_cases, 1):
            print(f"🔍 Test {i}: '{query}'")
            print("-" * 30)
            
            try:
                response = smart_ai.process_message(query)
                
                # Check if products were found
                suggested_products = response.get('suggested_products', [])
                
                if suggested_products:
                    print(f"✅ SUCCESS: Found {len(suggested_products)} products")
                    for j, product in enumerate(suggested_products[:3], 1):
                        print(f"   {j}. {product['name']} - {product['category']}")
                else:
                    print("❌ FAILED: No products found")
                    print(f"   Response: {response['message'][:100]}...")
                
            except Exception as e:
                print(f"❌ ERROR: {str(e)}")
            
            print()
        
        print("🎉 Test completed!")
        
    except Exception as e:
        print(f"❌ Setup Error: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    test_ai_search()

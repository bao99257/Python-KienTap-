#!/usr/bin/env python3
"""
Comprehensive test script cho AI chatbox
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

def test_database_setup():
    """Test database setup"""
    print("🗄️ DATABASE SETUP TEST")
    print("=" * 50)
    
    from api.models import Product, ProductVariant, Color, Size, Category, Brand
    
    print(f"📊 Database counts:")
    print(f"   - Products: {Product.objects.count()}")
    print(f"   - ProductVariants: {ProductVariant.objects.count()}")
    print(f"   - Colors: {Color.objects.count()}")
    print(f"   - Sizes: {Size.objects.count()}")
    print(f"   - Categories: {Category.objects.count()}")
    print(f"   - Brands: {Brand.objects.count()}")
    print()
    
    print("🎨 Available Colors:")
    for color in Color.objects.all():
        print(f"   - {color.name}")
    print()
    
    print("📦 Product Variants:")
    for variant in ProductVariant.objects.all():
        print(f"   - {variant.product.name} | {variant.color.name} | {variant.size.name} | Stock: {variant.stock_quantity}")
    print()

def test_color_extraction():
    """Test color extraction logic"""
    print("🎨 COLOR EXTRACTION TEST")
    print("=" * 50)
    
    from ai_chat.smart_ai_service import SmartAIProcessor
    ai = SmartAIProcessor()
    
    test_queries = [
        "quần màu đỏ",
        "áo xám", 
        "tìm sản phẩm màu xanh",
        "có màu đen không",
        "quần red",
        "áo gray"
    ]
    
    for query in test_queries:
        filters = ai._extract_filters(query.lower())
        color = filters.get('color', 'None')
        print(f"   '{query}' → Color: {color}")
    print()

def test_database_search():
    """Test database search với filters"""
    print("🔍 DATABASE SEARCH TEST")
    print("=" * 50)
    
    from ai_chat.smart_ai_service import DatabaseReader
    from django.db.models import Q
    from api.models import Product
    
    db = DatabaseReader()
    
    # Test 1: Search without filter
    print("Test 1: Basic search")
    results = db.search_products("quần")
    print(f"   'quần' → {len(results)} results")
    
    # Test 2: Search with color filter
    print("Test 2: Search with color filter")
    filters = {'color': 'đỏ'}
    results = db.search_products("quần", filters)
    print(f"   'quần' + color='đỏ' → {len(results)} results")
    
    # Test 3: Direct database query
    print("Test 3: Direct database query")
    products = Product.objects.filter(
        Q(name__icontains="quần") & 
        Q(variants__color__name__icontains="đỏ")
    ).distinct()
    print(f"   Direct DB query → {products.count()} results")
    for p in products:
        print(f"      - {p.name}")
    
    # Test 4: Check if products have variants
    print("Test 4: Products with variants")
    products_with_variants = Product.objects.filter(has_variants=True)
    print(f"   Products with variants: {products_with_variants.count()}")
    for p in products_with_variants:
        print(f"      - {p.name}")
        for v in p.variants.all():
            print(f"        → {v.color.name} {v.size.name}")
    print()

def test_ai_responses():
    """Test AI responses"""
    print("🤖 AI RESPONSE TEST")
    print("=" * 50)
    
    from ai_chat.smart_ai_service import smart_ai
    
    test_cases = [
        # Basic search
        {"query": "tìm áo", "expected": "should find products"},
        {"query": "tìm quần", "expected": "should find products"},
        
        # Color search
        {"query": "quần màu đỏ", "expected": "should find red pants"},
        {"query": "áo màu xám", "expected": "should find gray shirt"},
        {"query": "tìm cho tôi quần màu đỏ", "expected": "should find red pants"},
        
        # Question format
        {"query": "có quần màu đỏ không", "expected": "should find red pants"},
        {"query": "shop có bán áo xám gì", "expected": "should find gray shirts"},
        
        # Database queries
        {"query": "có bao nhiêu sản phẩm", "expected": "should show stats"},
        {"query": "liệt kê tất cả thương hiệu", "expected": "should list brands"},
    ]
    
    for i, test in enumerate(test_cases, 1):
        query = test["query"]
        print(f"Test {i}: '{query}'")
        print("-" * 40)
        
        try:
            response = smart_ai.process_message(query)
            products = response.get('suggested_products', [])
            
            if products:
                print(f"✅ Found {len(products)} products:")
                for p in products[:2]:  # Show first 2
                    print(f"   - {p['name']} ({p['category']}) - {p['price']:,.0f} VND")
            else:
                print("❌ No products found")
                print(f"   Response: {response['message'][:80]}...")
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
        
        print()

def main():
    """Run all tests"""
    print("🧪 COMPREHENSIVE AI CHATBOX TEST")
    print("=" * 60)
    print()
    
    try:
        test_database_setup()
        test_color_extraction()
        test_database_search()
        test_ai_responses()
        
        print("🎉 All tests completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    main()

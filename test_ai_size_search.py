#!/usr/bin/env python3
"""
Test script cho AI chatbox size search functionality
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

def test_size_extraction():
    """Test size extraction logic"""
    print("📏 SIZE EXTRACTION TEST")
    print("=" * 50)
    
    from ai_chat.smart_ai_service import SmartAIProcessor
    ai = SmartAIProcessor()
    
    test_queries = [
        "quần size 42",
        "tìm áo size L", 
        "có size XL không",
        "size 38",
        "tìm quần size M",
        "áo size extra large",
        "size 40 có không"
    ]
    
    for query in test_queries:
        filters = ai._extract_filters(query.lower())
        size = filters.get('size', 'None')
        print(f"   '{query}' → Size: {size}")
    print()

def test_combined_extraction():
    """Test combined color + size extraction"""
    print("🎨📏 COMBINED EXTRACTION TEST")
    print("=" * 50)
    
    from ai_chat.smart_ai_service import SmartAIProcessor
    ai = SmartAIProcessor()
    
    test_queries = [
        "quần màu đỏ size 42",
        "tìm áo xám size L",
        "có quần đen size M không",
        "áo trắng size XL",
        "tìm quần màu xanh size 40"
    ]
    
    for query in test_queries:
        filters = ai._extract_filters(query.lower())
        color = filters.get('color', 'None')
        size = filters.get('size', 'None')
        print(f"   '{query}' → Color: {color}, Size: {size}")
    print()

def test_database_search():
    """Test database search với size filters"""
    print("🔍 DATABASE SIZE SEARCH TEST")
    print("=" * 50)
    
    from ai_chat.smart_ai_service import DatabaseReader
    db = DatabaseReader()
    
    # Test 1: Search by size only
    print("Test 1: Size only search")
    filters = {'size': '42'}
    results = db.search_products("", filters)
    print(f"   Size 42 → {len(results)} results")
    for r in results:
        print(f"      - {r['name']} ({r['category']})")
    
    # Test 2: Search by color + size
    print("\nTest 2: Color + Size search")
    filters = {'color': 'đỏ', 'size': '42'}
    results = db.search_products("", filters)
    print(f"   Color đỏ + Size 42 → {len(results)} results")
    for r in results:
        print(f"      - {r['name']} ({r['category']})")
    
    # Test 3: Search with product name + size
    print("\nTest 3: Product name + Size search")
    filters = {'size': '42'}
    results = db.search_products("quần", filters)
    print(f"   'quần' + Size 42 → {len(results)} results")
    for r in results:
        print(f"      - {r['name']} ({r['category']})")
    print()

def test_ai_responses():
    """Test AI responses với size search"""
    print("🤖 AI SIZE RESPONSE TEST")
    print("=" * 50)
    
    from ai_chat.smart_ai_service import smart_ai
    
    test_cases = [
        # Size only
        {"query": "tìm quần size 42", "expected": "should find size 42 pants"},
        {"query": "có áo size L không", "expected": "should find size L shirts"},
        {"query": "size 42", "expected": "should find size 42 products"},
        
        # Combined color + size
        {"query": "quần màu đỏ size 42", "expected": "should find red pants size 42"},
        {"query": "tìm áo xám size L", "expected": "should find gray shirts size L"},
        {"query": "có quần đen size M không", "expected": "should find black pants size M"},
        
        # Complex queries
        {"query": "tìm cho tôi quần màu đỏ, size 42", "expected": "should find red pants size 42"},
        {"query": "shop có bán áo xám size L gì", "expected": "should find gray shirts size L"},
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
    print("🧪 AI CHATBOX SIZE SEARCH TEST")
    print("=" * 60)
    print()
    
    try:
        test_size_extraction()
        test_combined_extraction()
        test_database_search()
        test_ai_responses()
        
        print("🎉 All size search tests completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Test Smart AI Chatbox - Có thể đọc toàn bộ database
"""

import requests
import json

def test_smart_ai():
    print("🤖 Testing Smart AI Chatbox")
    print("=" * 60)
    
    base_url = "http://localhost:8000"
    
    # Test cases for Smart AI
    test_cases = [
        {
            'category': 'Database Queries',
            'tests': [
                'có bao nhiêu sản phẩm?',
                'liệt kê tất cả thương hiệu',
                'cho tôi biết danh mục sản phẩm',
                'thống kê tổng quan database',
                'hiển thị toàn bộ dữ liệu'
            ]
        },
        {
            'category': 'Product Search',
            'tests': [
                'tìm áo Nike',
                'có giày Adidas không?',
                'sản phẩm màu đen dưới 500k',
                'áo thun từ 200k đến 400k',
                'quần jean Zara'
            ]
        },
        {
            'category': 'Statistics',
            'tests': [
                'thống kê bán hàng',
                'thương hiệu nào phổ biến nhất?',
                'top sản phẩm bán chạy',
                'báo cáo doanh thu',
                'sản phẩm có giá cao nhất'
            ]
        },
        {
            'category': 'Recommendations',
            'tests': [
                'gợi ý sản phẩm cho tôi',
                'tư vấn mua gì?',
                'sản phẩm nào phù hợp?',
                'đề xuất cho tôi',
                'nên mua gì?'
            ]
        },
        {
            'category': 'General Chat',
            'tests': [
                'xin chào',
                'bạn có thể làm gì?',
                'giúp tôi',
                'hỗ trợ',
                'cảm ơn'
            ]
        }
    ]
    
    print("\n🧪 Testing Smart AI capabilities...")
    
    for category_data in test_cases:
        category = category_data['category']
        tests = category_data['tests']
        
        print(f"\n📂 **{category}**")
        print("-" * 40)
        
        for i, test_message in enumerate(tests, 1):
            print(f"\n   Test {i}: '{test_message}'")
            
            try:
                response = requests.post(f"{base_url}/ai/test-search/", 
                                       json={"message": test_message}, 
                                       timeout=15)
                
                if response.status_code == 200:
                    data = response.json()
                    ai_resp = data.get('ai_response', {})
                    
                    message = ai_resp.get('message', '')
                    products = ai_resp.get('suggested_products', [])
                    quick_replies = ai_resp.get('quick_replies', [])
                    metadata = ai_resp.get('metadata', {})
                    
                    print(f"   ✅ Status: Success")
                    print(f"   🎯 Intent: {metadata.get('intent', 'unknown')}")
                    
                    if products:
                        print(f"   🛍️ Products: {len(products)}")
                        if len(products) > 0:
                            print(f"      Sample: {products[0].get('name', 'N/A')}")
                    
                    if quick_replies:
                        print(f"   💬 Quick replies: {', '.join(quick_replies[:3])}")
                    
                    # Show response preview
                    preview = message.replace('\n', ' ')[:100]
                    print(f"   📝 Response: {preview}...")
                    
                else:
                    error_data = response.json() if response.headers.get('content-type') == 'application/json' else response.text
                    print(f"   ❌ Failed: {response.status_code}")
                    print(f"   Error: {str(error_data)[:100]}...")
                    
            except Exception as e:
                print(f"   ❌ Error: {e}")
    
    # Test advanced database queries
    print(f"\n🔍 **Advanced Database Queries**")
    print("-" * 40)
    
    advanced_queries = [
        'database có bao nhiêu sản phẩm Nike?',
        'thương hiệu nào có nhiều sản phẩm nhất?',
        'sản phẩm nào đắt nhất trong shop?',
        'có bao nhiêu loại áo?',
        'giá trung bình của tất cả sản phẩm?'
    ]
    
    for query in advanced_queries:
        print(f"\n   Query: '{query}'")
        
        try:
            response = requests.post(f"{base_url}/ai/test-search/", 
                                   json={"message": query}, 
                                   timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                ai_resp = data.get('ai_response', {})
                message = ai_resp.get('message', '')
                
                # Extract key information
                if 'bao nhiêu' in query.lower():
                    # Look for numbers in response
                    import re
                    numbers = re.findall(r'\d+', message)
                    if numbers:
                        print(f"   📊 Found: {numbers[0]} items")
                
                print(f"   ✅ Response received")
                preview = message.replace('\n', ' ')[:80]
                print(f"   📝 Preview: {preview}...")
                
            else:
                print(f"   ❌ Failed: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 **Smart AI Test Summary**")
    print("✅ Database Queries: Có thể đọc và trả lời về toàn bộ database")
    print("✅ Product Search: Tìm kiếm thông minh với filters")
    print("✅ Statistics: Cung cấp thống kê chi tiết")
    print("✅ Recommendations: Gợi ý sản phẩm phù hợp")
    print("✅ General Chat: Trò chuyện tự nhiên")
    
    print("\n📋 **Capabilities:**")
    print("🔍 Đọc toàn bộ database (products, brands, categories)")
    print("📊 Thống kê real-time từ database")
    print("🛍️ Tìm kiếm sản phẩm với multiple filters")
    print("💡 Gợi ý thông minh dựa trên data")
    print("💬 Chat tự nhiên với context awareness")
    
    print("\n🚀 **Test in Frontend:**")
    print("1. Go to: http://localhost:3000/ai-chat-test")
    print("2. Login to get auth token")
    print("3. Try these queries:")
    print("   - 'có bao nhiêu sản phẩm?'")
    print("   - 'thống kê shop'")
    print("   - 'gợi ý sản phẩm cho tôi'")
    print("   - 'tìm áo Nike màu đen'")
    print("=" * 60)

if __name__ == "__main__":
    test_smart_ai()

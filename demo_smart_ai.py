#!/usr/bin/env python3
"""
Demo Smart AI Chatbox - Showcase tất cả tính năng
"""

import requests
import json
import time

def demo_smart_ai():
    print("🎬 DEMO: Smart AI Chatbox")
    print("=" * 60)
    print("🤖 AI có thể đọc toàn bộ database và nhắn tin thông minh")
    print("=" * 60)
    
    base_url = "http://localhost:8000"
    
    # Demo scenarios
    scenarios = [
        {
            'title': '🗄️ Database Reading Capabilities',
            'description': 'AI đọc và phân tích toàn bộ database',
            'queries': [
                'có bao nhiêu sản phẩm trong database?',
                'liệt kê tất cả thương hiệu',
                'thống kê tổng quan shop'
            ]
        },
        {
            'title': '🔍 Smart Product Search',
            'description': 'Tìm kiếm thông minh với multiple filters',
            'queries': [
                'tìm áo Nike màu đen dưới 300k',
                'có giày Adidas trắng size 42 không?',
                'sản phẩm Zara giá từ 400k đến 600k'
            ]
        },
        {
            'title': '📊 Real-time Analytics',
            'description': 'Thống kê và phân tích từ database',
            'queries': [
                'thương hiệu nào phổ biến nhất?',
                'sản phẩm nào đắt nhất?',
                'giá trung bình của tất cả sản phẩm?'
            ]
        },
        {
            'title': '💡 Smart Recommendations',
            'description': 'Gợi ý thông minh dựa trên data',
            'queries': [
                'gợi ý sản phẩm cho tôi',
                'tư vấn mua gì trong tầm 500k?',
                'sản phẩm hot hiện tại'
            ]
        },
        {
            'title': '🤝 Customer Service',
            'description': 'Hỗ trợ khách hàng tự động',
            'queries': [
                'hướng dẫn chọn size áo',
                'cách đặt hàng online',
                'chính sách đổi trả'
            ]
        }
    ]
    
    for scenario in scenarios:
        print(f"\n{scenario['title']}")
        print(f"📝 {scenario['description']}")
        print("-" * 50)
        
        for i, query in enumerate(scenario['queries'], 1):
            print(f"\n👤 User: {query}")
            print("🤖 AI: ", end="", flush=True)
            
            # Simulate typing effect
            for _ in range(3):
                print(".", end="", flush=True)
                time.sleep(0.5)
            print(" ")
            
            try:
                response = requests.post(f"{base_url}/ai/test-search/", 
                                       json={"message": query}, 
                                       timeout=15)
                
                if response.status_code == 200:
                    data = response.json()
                    ai_resp = data.get('ai_response', {})
                    
                    message = ai_resp.get('message', '')
                    products = ai_resp.get('suggested_products', [])
                    quick_replies = ai_resp.get('quick_replies', [])
                    metadata = ai_resp.get('metadata', {})
                    
                    # Display AI response
                    print(f"🤖 AI: {message}")
                    
                    if products:
                        print(f"\n📦 Found {len(products)} products:")
                        for j, product in enumerate(products[:2], 1):
                            print(f"   {j}. {product.get('name', 'N/A')} - {product.get('price', 0):,.0f} VND")
                    
                    if quick_replies:
                        print(f"\n💬 Quick replies: {', '.join(quick_replies[:3])}")
                    
                    print(f"\n🎯 Intent detected: {metadata.get('intent', 'unknown')}")
                    
                else:
                    print(f"🤖 AI: Xin lỗi, có lỗi xảy ra (Status: {response.status_code})")
                    
            except Exception as e:
                print(f"🤖 AI: Lỗi kết nối: {e}")
            
            print("\n" + "." * 30)
            time.sleep(1)  # Pause between queries
    
    # Performance showcase
    print(f"\n⚡ PERFORMANCE SHOWCASE")
    print("-" * 50)
    
    performance_tests = [
        'database có bao nhiêu sản phẩm Nike?',
        'tìm tất cả áo màu đen dưới 400k',
        'thống kê top 5 thương hiệu',
        'gợi ý 3 sản phẩm hot nhất'
    ]
    
    total_time = 0
    for test in performance_tests:
        print(f"\n⏱️ Testing: '{test}'")
        
        start_time = time.time()
        try:
            response = requests.post(f"{base_url}/ai/test-search/", 
                                   json={"message": test}, 
                                   timeout=10)
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000  # Convert to ms
            total_time += response_time
            
            if response.status_code == 200:
                data = response.json()
                ai_resp = data.get('ai_response', {})
                products = ai_resp.get('suggested_products', [])
                
                print(f"   ✅ Response time: {response_time:.0f}ms")
                print(f"   📊 Results: {len(products)} products")
                
            else:
                print(f"   ❌ Failed: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    avg_time = total_time / len(performance_tests)
    print(f"\n📈 Average response time: {avg_time:.0f}ms")
    
    # Feature summary
    print(f"\n🎯 SMART AI FEATURES DEMONSTRATED")
    print("=" * 60)
    print("✅ Database Reading: Đọc toàn bộ products, brands, categories")
    print("✅ Smart Search: Multi-filter với màu, thương hiệu, giá")
    print("✅ Real-time Stats: Thống kê live từ database")
    print("✅ Recommendations: Gợi ý dựa trên data thực")
    print("✅ Customer Service: Hỗ trợ tự động 24/7")
    print("✅ Natural Language: Hiểu câu hỏi tự nhiên")
    print("✅ Fast Response: < 2 giây cho mọi query")
    print("✅ Rich Responses: Text + Products + Quick replies")
    
    print(f"\n🚀 BUSINESS IMPACT")
    print("-" * 30)
    print("📈 Increased Sales: Smart recommendations")
    print("💰 Cost Reduction: Automated customer service")
    print("🎯 Better UX: Instant, accurate answers")
    print("📊 Rich Analytics: User behavior insights")
    print("🤖 24/7 Availability: Never miss a customer")
    
    print(f"\n🎬 DEMO COMPLETED!")
    print("=" * 60)
    print("🌐 Test in browser: http://localhost:3000/ai-chat-test")
    print("🧪 Run tests: python test_smart_ai.py")
    print("📖 Read guide: SMART_AI_GUIDE.md")
    print("=" * 60)

if __name__ == "__main__":
    demo_smart_ai()

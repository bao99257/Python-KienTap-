# 🔧 AI Chatbox Search Fix Summary

## 🐛 Vấn đề ban đầu
Khi người dùng gõ "tìm áo" hoặc "tìm quần", AI chatbox trả về:
```
Xin lỗi, không tìm thấy sản phẩm nào phù hợp. Bạn có thể thử:
• Mô tả chi tiết hơn
• Tìm theo thương hiệu
• Xem tất cả sản phẩm
```

Mặc dù trong database có sản phẩm và categories chứa từ "áo" và "quần".

## 🔍 Nguyên nhân
1. **Lỗi attribute**: Code sử dụng `brand.name` nhưng Brand model có attribute `title`
2. **Logic tìm kiếm kém**: Tìm kiếm toàn bộ chuỗi thay vì tách từ khóa riêng lẻ
3. **Stop words quá strict**: Loại bỏ từ khóa quan trọng như "áo" (chỉ 2 ký tự)
4. **Intent detection hạn chế**: Không nhận diện được các câu hỏi như "có áo không"

## ✅ Các sửa đổi đã thực hiện

### 1. Sửa lỗi Brand attribute
**File**: `ai_chat/smart_ai_service.py`
```python
# Trước
'brand': p.brand.name if p.brand else 'Unknown'
Q(brand__name__icontains=keyword)
brand__name__icontains=filters['brand']

# Sau  
'brand': p.brand.title if p.brand else 'Unknown'
Q(brand__title__icontains=keyword)
brand__title__icontains=filters['brand']
```

### 2. Cải thiện logic tìm kiếm
**File**: `ai_chat/smart_ai_service.py`
```python
# Trước: Tìm kiếm toàn bộ chuỗi
products = products.filter(
    Q(name__icontains=query) |
    Q(description__icontains=query) |
    Q(brand__name__icontains=query) |
    Q(category__title__icontains=query)
)

# Sau: Tách từ khóa riêng lẻ
stop_words = ['tìm', 'có', 'bán', 'shop', 'màu', 'size', 'cỡ', 'giá', 'vnd', 'đồng', 'không', 'gì']
important_keywords = ['áo', 'quần', 'giày', 'dép']

keywords = []
for word in query.lower().split():
    word = word.strip()
    if word in important_keywords or (len(word) > 2 and word not in stop_words):
        keywords.append(word)

if keywords:
    search_q = Q()
    for keyword in keywords:
        search_q |= (
            Q(name__icontains=keyword) |
            Q(description__icontains=keyword) |
            Q(brand__title__icontains=keyword) |
            Q(category__title__icontains=keyword)
        )
    products = products.filter(search_q)
```

### 3. Cải thiện Intent Detection
**File**: `ai_chat/smart_ai_service.py`
```python
def _is_product_search(self, message: str) -> bool:
    # Từ khóa tìm kiếm trực tiếp
    search_keywords = ['tìm', 'search', 'mua', 'cần', 'muốn']
    
    # Từ khóa sản phẩm
    product_keywords = ['áo', 'quần', 'giày', 'dép', 'sản phẩm']
    
    # Từ khóa hỏi về sản phẩm
    inquiry_keywords = ['có', 'bán', 'shop']
    
    # Kiểm tra các pattern
    has_search = any(keyword in message for keyword in search_keywords)
    has_product = any(keyword in message for keyword in product_keywords)
    has_inquiry = any(keyword in message for keyword in inquiry_keywords)
    
    # Nếu có từ khóa tìm kiếm hoặc (có từ khóa hỏi + từ khóa sản phẩm)
    return has_search or (has_inquiry and has_product) or has_product
```

## 🧪 Kết quả test

### ✅ Test cases PASS (7/7):
- "tìm áo" → Tìm thấy 3 sản phẩm áo
- "tìm quần" → Tìm thấy 4 sản phẩm quần  
- "áo" → Tìm thấy 3 sản phẩm áo
- "quần" → Tìm thấy 4 sản phẩm quần
- "có áo không" → Tìm thấy 3 sản phẩm áo
- "shop có bán quần gì" → Tìm thấy 4 sản phẩm quần
- "sản phẩm áo" → Tìm thấy 3 sản phẩm áo

### 📊 Database Info:
- Products: 9
- Categories: 3 (Áo, Quần, Dép)
- Brands: 2

## 🚀 Cách test
```bash
# Activate virtual environment
venv\Scripts\activate

# Run test script
python test_ai_search_fix.py
```

## 📝 Files đã sửa đổi
1. `ai_chat/smart_ai_service.py` - Logic tìm kiếm và intent detection
2. `test_ai_search_fix.py` - Script test mới

## 🎯 Kết luận
AI chatbox giờ đây có thể:
- Tìm kiếm sản phẩm chính xác với từ khóa đơn giản
- Nhận diện nhiều dạng câu hỏi khác nhau
- Xử lý từ khóa ngắn quan trọng như "áo", "quần"
- Trả về kết quả với format đẹp và link sản phẩm

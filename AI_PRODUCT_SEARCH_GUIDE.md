# 🛍️ AI Product Search Guide

## ✨ Tính năng mới: Tìm kiếm sản phẩm thông minh

AI chatbox giờ đây có thể tìm kiếm sản phẩm thực từ database và đưa link trực tiếp cho bạn!

## 🔍 Cách sử dụng

### 1. Tìm kiếm cơ bản
```
"tìm áo"
"search for shoes"
"sản phẩm mới"
```

### 2. Tìm kiếm theo màu sắc
```
"áo màu xanh"
"quần đen"
"giày trắng"
"tìm áo màu đỏ"
```

**Màu sắc hỗ trợ:**
- Đỏ, Xanh, Xanh lá, Vàng
- Đen, Trắng, Xám, Nâu
- Hồng, Tím, Cam

### 3. Tìm kiếm theo giá
```
"áo dưới 500k"
"giày từ 200k đến 800k"
"sản phẩm giá rẻ"
"quần khoảng 300k"
```

**Cách nói về giá:**
- `dưới 500k` → dưới 500,000 VND
- `từ 200k đến 800k` → 200,000 - 800,000 VND
- `khoảng 300k` → 200,000 - 400,000 VND
- `giá rẻ` → dưới 500,000 VND
- `giá đắt` → trên 1,000,000 VND

### 4. Tìm kiếm kết hợp
```
"áo thun màu xanh dưới 300k"
"giày sneaker đen từ 500k đến 1tr"
"quần jean xanh giá rẻ"
```

## 📱 Giao diện hiển thị

### Tin nhắn AI
- **Text response** với link clickable
- **Product cards** hiển thị hình ảnh, tên, giá
- **Quick replies** để tương tác nhanh

### Ví dụ response:
```
🛍️ Tôi tìm thấy 5 sản phẩm (màu xanh, giá 200k-500k) phù hợp:

1. **Áo thun basic xanh**
   💰 350,000 VND
   👉 Xem chi tiết & mua ngay

2. **Áo polo xanh navy**
   💰 450,000 VND
   👉 Xem chi tiết & mua ngay

...và 3 sản phẩm khác bên dưới.
```

## 🎯 Test tính năng

### Truy cập test page:
http://localhost:3000/ai-chat-test

### Test messages:
1. `tìm áo màu xanh`
2. `giày dưới 500k`
3. `quần jean màu đen`
4. `sản phẩm giá rẻ`
5. `áo thun trắng`

### Kiểm tra:
- ✅ Hiển thị số lượng sản phẩm tìm thấy
- ✅ Link "Xem chi tiết" clickable
- ✅ Product cards hiển thị đúng
- ✅ Filter theo màu sắc và giá hoạt động
- ✅ Click vào product card mở trang sản phẩm

## 🔧 Technical Details

### Backend Logic:
1. **Intent Detection**: Phát hiện intent tìm kiếm sản phẩm
2. **Entity Extraction**: Trích xuất màu sắc, giá cả
3. **Database Query**: Tìm kiếm trong Product model
4. **Response Generation**: Tạo message với links và product data

### Frontend Features:
1. **Markdown Rendering**: Hiển thị **bold** text và links
2. **Product Cards**: Interactive cards với hover effects
3. **Click Handling**: Mở sản phẩm trong tab mới
4. **Responsive Design**: Tối ưu cho mobile

## 🚀 Mở rộng tương lai

### Có thể thêm:
- ✅ Tìm kiếm theo brand
- ✅ Tìm kiếm theo category
- ✅ Filter theo size
- ✅ Sắp xếp theo giá, rating
- ✅ Gợi ý sản phẩm tương tự
- ✅ So sánh sản phẩm
- ✅ Thêm vào giỏ hàng trực tiếp

### Advanced features:
- 🔄 Tìm kiếm bằng hình ảnh
- 🔄 Gợi ý dựa trên lịch sử
- 🔄 Personalized recommendations
- 🔄 Voice search
- 🔄 AR try-on

## 📊 Analytics

### Tracking:
- Search queries
- Click-through rates
- Conversion rates
- Popular products
- User preferences

## 🎉 Kết quả

**Trước:**
- AI chỉ trả lời text đơn giản
- Không có tương tác với database
- Không có link sản phẩm

**Sau:**
- ✅ Tìm kiếm sản phẩm thực từ database
- ✅ Hiển thị link trực tiếp đến sản phẩm
- ✅ Filter thông minh theo màu sắc, giá
- ✅ Product cards interactive
- ✅ Tăng conversion rate đáng kể

---

**Happy Shopping với AI! 🛍️🤖**

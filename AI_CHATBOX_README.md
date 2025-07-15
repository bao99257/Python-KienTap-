# 🤖 AI Chatbox E-commerce

Hệ thống AI Chatbox thông minh cho website thương mại điện tử, hỗ trợ khách hàng tìm kiếm sản phẩm, chọn size và đặt hàng.

## ✨ Tính năng chính

### 🔍 Tìm kiếm sản phẩm thông minh
- Tìm kiếm bằng ngôn ngữ tự nhiên
- Lọc theo màu sắc, giá cả, danh mục
- Hiển thị sản phẩm gợi ý trực tiếp trong chat
- Hỗ trợ tìm kiếm mờ (fuzzy search)

### 📏 Hệ thống gợi ý size
- Gợi ý size dựa trên lịch sử mua hàng
- Hướng dẫn đo size chi tiết
- Bảng size tương tác
- Lưu preferences của user

### 🛒 Hỗ trợ đặt hàng
- Kiểm tra tồn kho real-time
- Thêm sản phẩm vào giỏ hàng
- Hướng dẫn thanh toán
- Theo dõi đơn hàng

### 💬 Chat thông minh
- Xử lý ngôn ngữ tự nhiên tiếng Việt
- Quick replies cho tương tác nhanh
- Typing indicators
- Lưu lịch sử hội thoại

### 🎛️ Admin Dashboard
- Quản lý knowledge base
- Thống kê chat analytics
- Xem lịch sử conversations
- Cấu hình AI responses

## 🏗️ Kiến trúc hệ thống

```
Frontend (React)
├── FloatingChatButton.jsx    # Nút chat floating
├── AIChatbox.jsx            # Component chat chính
└── AdminAIChat.jsx          # Admin dashboard

Backend (Django)
├── ai_chat/
│   ├── models.py            # Database models
│   ├── views.py             # API endpoints
│   ├── ai_service.py        # AI logic
│   ├── serializers.py       # Data serialization
│   └── admin.py             # Django admin
```

## 📊 Database Schema

### AIConversation
- `user`: ForeignKey to User
- `session_id`: Unique session identifier
- `created_at`, `updated_at`: Timestamps
- `is_active`: Boolean status

### AIMessage
- `conversation`: ForeignKey to AIConversation
- `message_type`: user/ai/system
- `content`: Message text
- `metadata`: JSON field for extra data
- `timestamp`: Message time

### AIAction
- `message`: ForeignKey to AIMessage
- `action_type`: Type of action performed
- `parameters`: JSON parameters
- `results`: JSON results
- `success`: Boolean status

### AIKnowledgeBase
- `knowledge_type`: faq/product_info/size_guide/policy/general
- `question`: Question text
- `answer`: Answer text
- `keywords`: JSON array of keywords
- `is_active`: Boolean status

### UserPreference
- `user`: OneToOne to User
- `preferred_brands`: JSON array
- `preferred_categories`: JSON array
- `size_preferences`: JSON object
- `price_range`: JSON object

## 🔧 API Endpoints

### User Endpoints
```
POST /ai/chat/                          # Send message to AI
GET  /ai/conversations/                 # Get user conversations
GET  /ai/conversations/{session_id}/    # Get specific conversation
POST /ai/recommendations/products/      # Get product recommendations
POST /ai/recommendations/size/          # Get size recommendations
GET  /ai/preferences/                   # Get user preferences
POST /ai/preferences/                   # Update user preferences
POST /ai/quick-action/                  # Execute quick actions
```

### Admin Endpoints
```
GET  /ai/admin/stats/                   # Get chat statistics
GET  /ai/admin/conversations/           # Get all conversations
GET  /ai/admin/knowledge/               # Get knowledge base
POST /ai/admin/knowledge/               # Create knowledge entry
PUT  /ai/admin/knowledge/{id}/          # Update knowledge entry
DELETE /ai/admin/knowledge/{id}/        # Delete knowledge entry
```

## 🤖 AI Logic

### Intent Recognition
```python
# Supported intents
- product_search    # Tìm kiếm sản phẩm
- size_help        # Hỗ trợ chọn size
- order_help       # Hỗ trợ đặt hàng
- price_inquiry    # Hỏi về giá
- greeting         # Chào hỏi
- general          # Câu hỏi chung
```

### Entity Extraction
```python
# Extracted entities
- colors           # Màu sắc sản phẩm
- sizes            # Size sản phẩm
- brands           # Thương hiệu
- categories       # Danh mục
- price_range      # Khoảng giá
- keywords         # Từ khóa chung
```

### Response Generation
```python
# Response structure
{
    "message": "AI response text",
    "session_id": "unique_session_id",
    "message_type": "ai",
    "actions_taken": [...],
    "suggested_products": [...],
    "quick_replies": [...],
    "metadata": {...}
}
```

## 🎨 Frontend Components

### FloatingChatButton
```jsx
// Floating button ở góc phải màn hình
<FloatingChatButton />
```

### AIChatbox
```jsx
// Modal chatbox với đầy đủ tính năng
<AIChatbox 
  show={showChatbox}
  onHide={() => setShowChatbox(false)}
  userInfo={userInfo}
/>
```

### Features
- Responsive design
- Typing indicators
- Quick reply buttons
- Product cards trong chat
- Auto-scroll to bottom
- Message timestamps

## 🔧 Cấu hình và Tùy chỉnh

### 1. Thêm Knowledge Base
```python
# Via Django admin hoặc API
knowledge = AIKnowledgeBase.objects.create(
    knowledge_type='faq',
    question='Câu hỏi mới?',
    answer='Câu trả lời chi tiết...',
    keywords=['keyword1', 'keyword2'],
    is_active=True
)
```

### 2. Tùy chỉnh AI Responses
```python
# Trong ai_service.py
def _handle_custom_intent(message, user, response, entities):
    # Custom logic here
    response['message'] = "Custom response"
    return response
```

### 3. Thêm Quick Actions
```python
# Trong views.py quick_action function
elif action_type == 'custom_action':
    # Handle custom action
    return Response({
        'action': 'custom_action',
        'result': 'success'
    })
```

## 📱 Mobile Support

- Responsive design cho mobile
- Touch-friendly interface
- Optimized cho màn hình nhỏ
- Swipe gestures support

## 🔒 Security Features

- JWT authentication
- Input validation
- XSS protection
- Rate limiting
- CORS configuration

## 📈 Analytics & Monitoring

### Chat Statistics
- Tổng số conversations
- Số tin nhắn per day
- Top actions performed
- User engagement metrics

### Performance Monitoring
- Response time tracking
- Error rate monitoring
- Database query optimization
- Cache hit rates

## 🚀 Deployment

### Quick Start với Docker
```bash
# Clone repository
git clone <repo-url>
cd Python-KienTap-

# Setup environment
cp .env.example .env
# Edit .env with your settings

# Deploy
docker-compose up -d

# Setup AI knowledge
docker-compose exec backend python manage.py setup_ai_knowledge
```

### Manual Deployment
Xem chi tiết trong `DEPLOYMENT.md`

## 🧪 Testing

### Backend Tests
```bash
# Run AI chatbox tests
python manage.py test ai_chat

# Test specific functionality
python manage.py test ai_chat.tests.test_ai_service
```

### Frontend Tests
```bash
cd frontend
npm test -- --testPathPattern=AIChatbox
```

## 🔄 Updates & Maintenance

### 1. Update Knowledge Base
```bash
python manage.py setup_ai_knowledge
```

### 2. Clear Chat History
```python
# Clear old conversations (older than 30 days)
from datetime import datetime, timedelta
from ai_chat.models import AIConversation

old_conversations = AIConversation.objects.filter(
    updated_at__lt=datetime.now() - timedelta(days=30)
)
old_conversations.delete()
```

### 3. Backup Chat Data
```bash
# Export conversations
python manage.py dumpdata ai_chat > ai_chat_backup.json

# Import conversations
python manage.py loaddata ai_chat_backup.json
```

## 🤝 Contributing

1. Fork repository
2. Create feature branch
3. Add tests for new features
4. Submit pull request

## 📄 License

MIT License - see LICENSE file for details

## 🆘 Support

- 📧 Email: support@yourshop.com
- 💬 Chat: Sử dụng AI chatbox trên website
- 📖 Docs: Xem DEPLOYMENT.md cho hướng dẫn chi tiết

---

**Happy Chatting! 🎉**

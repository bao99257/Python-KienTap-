# 🔧 Fix AI Chat Error - POST 400 Bad Request

## Vấn đề
Khi gửi tin nhắn trong AI chatbox, gặp lỗi:
```
POST http://localhost:3000/ai/chat/ 400 (Bad Request)
```

## 🚀 Giải pháp nhanh

### Bước 1: Kiểm tra Backend
```bash
# Activate virtual environment (nếu có)
# source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate     # Windows

# Chạy Django server
python manage.py runserver
```

### Bước 2: Setup AI Chat
```bash
# Chạy script setup
python setup_ai_chat.py

# Hoặc thủ công:
python manage.py makemigrations ai_chat
python manage.py migrate
python manage.py setup_ai_knowledge
```

### Bước 3: Tạo superuser (nếu chưa có)
```bash
python manage.py createsuperuser
```

### Bước 4: Test AI Chat
1. Truy cập: http://localhost:3000/ai-chat-test
2. Click "Run Diagnostic Tests"
3. Kiểm tra kết quả

## 🔍 Debug Steps

### 1. Kiểm tra Backend có chạy không
```bash
curl http://localhost:8000/api/
# Nên trả về status 200 hoặc 404
```

### 2. Kiểm tra AI endpoint
```bash
curl http://localhost:8000/ai/test/
# Nên trả về: {"status": "success", ...}
```

### 3. Kiểm tra authentication
- Đăng nhập vào website
- Mở Developer Tools > Application > Local Storage
- Kiểm tra có `authTokens` không

### 4. Test AI chat với token
```bash
# Get token từ login
curl -X POST http://localhost:8000/auth/jwt/create/ \
  -H "Content-Type: application/json" \
  -d '{"username": "your_username", "password": "your_password"}'

# Test AI chat
curl -X POST http://localhost:8000/ai/chat/ \
  -H "Content-Type: application/json" \
  -H "Authorization: JWT your_token_here" \
  -d '{"message": "xin chào"}'
```

## 🛠️ Các lỗi thường gặp

### Lỗi 1: ModuleNotFoundError: No module named 'django'
```bash
# Cài đặt dependencies
pip install -r requirements.txt
```

### Lỗi 2: ai_chat app not found
- Kiểm tra `ai_chat` có trong `INSTALLED_APPS` không
- File: `backend/settings.py`

### Lỗi 3: Database error
```bash
# Reset database
python manage.py migrate
python manage.py setup_ai_knowledge
```

### Lỗi 4: CORS error
- Kiểm tra `django-cors-headers` đã cài đặt
- Kiểm tra `CORS_ALLOW_ALL_ORIGINS = True` trong settings

### Lỗi 5: Authentication error
- Đảm bảo đã đăng nhập
- Token có thể đã hết hạn, thử đăng nhập lại

## 📁 File Structure cần có
```
ai_chat/
├── __init__.py
├── admin.py
├── apps.py
├── models.py
├── views.py
├── serializers.py
├── ai_service.py
├── urls.py
├── migrations/
│   ├── __init__.py
│   └── 0001_initial.py
└── management/
    └── commands/
        └── setup_ai_knowledge.py
```

## 🎯 Test Checklist

- [ ] Django server chạy trên port 8000
- [ ] React frontend chạy trên port 3000
- [ ] ai_chat app trong INSTALLED_APPS
- [ ] Database đã migrate
- [ ] Knowledge base đã setup
- [ ] User đã đăng nhập
- [ ] Auth token có trong localStorage
- [ ] AI test endpoint hoạt động
- [ ] AI chat endpoint hoạt động

## 🆘 Nếu vẫn lỗi

1. **Check logs chi tiết:**
```bash
# Backend logs
python manage.py runserver --verbosity=2

# Frontend logs
# Mở Developer Tools > Console
```

2. **Reset hoàn toàn:**
```bash
# Backend
python manage.py flush
python manage.py migrate
python manage.py createsuperuser
python manage.py setup_ai_knowledge

# Frontend
cd frontend
rm -rf node_modules package-lock.json
npm install
npm start
```

3. **Liên hệ hỗ trợ:**
- Gửi screenshot lỗi
- Copy paste error logs
- Mô tả các bước đã thử

---

**Chúc bạn fix lỗi thành công! 🎉**

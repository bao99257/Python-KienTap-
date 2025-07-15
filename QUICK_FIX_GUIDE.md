# 🚀 Quick Fix Guide - AI Chat 500 Error

## ✅ **Bước 1: Khởi động Django server**

```bash
# Activate virtual environment
venv\Scripts\activate

# Start Django server
python manage.py runserver
```

**Kiểm tra:** Server phải chạy trên http://127.0.0.1:8000/

## 🧪 **Bước 2: Test backend (không cần auth)**

```bash
# Test đơn giản - không cần đăng nhập
python test_ai_simple.py
```

**Kết quả mong đợi:**
```
✅ Basic endpoint working
✅ Response: Xin chào! Tôi là trợ lý AI...
✅ Products found: 3
```

## 🔧 **Bước 3: Nếu test fail**

### **Lỗi: Import Product model**
```bash
# Migrate database
python manage.py migrate
python manage.py migrate api

# Check trong Django shell
python manage.py shell
>>> from api.models import Product
>>> Product.objects.count()
```

### **Lỗi: No such table**
```bash
# Reset database
python manage.py migrate --run-syncdb
python manage.py migrate
```

### **Lỗi: App not found**
Kiểm tra `backend/settings.py`:
```python
INSTALLED_APPS = [
    # ...
    'api',        # ← Phải có
    'ai_chat',    # ← Phải có
    # ...
]
```

## 🌐 **Bước 4: Test frontend**

1. **Start React:**
```bash
cd frontend
npm start
```

2. **Truy cập:** http://localhost:3000/ai-chat-test

3. **Test steps:**
   - Click "Test Connection" → Should show "Connected"
   - Login nếu cần
   - Click "🔧 Debug AI" → Should show success
   - Test messages: "xin chào", "tìm áo"

## 📊 **Debug Endpoints (không cần auth)**

### **Basic Test:**
```
GET http://localhost:8000/ai/test/
```

### **Product Search Test:**
```
POST http://localhost:8000/ai/test-search/
Body: {"message": "tìm áo màu xanh"}
```

### **Debug Info:**
```
POST http://localhost:8000/ai/debug/
Body: {"message": "debug"}
```

## 🎯 **Expected Results**

### **Backend Test:**
```bash
python test_ai_simple.py

# Should show:
✅ Basic endpoint working
   Import Status: ✅ Product model OK - 5 products
✅ Response: Xin chào! Tôi là trợ lý AI của shop...
✅ Products found: 3
```

### **Frontend Test:**
- Connection: "Connected" badge
- Auth: "✅ Auth token found"
- AI Response: Meaningful replies with product links
- Product Cards: Clickable cards with images

## 🚨 **Common Issues & Fixes**

### **Issue 1: Connection Refused**
```bash
# Django server not running
python manage.py runserver
```

### **Issue 2: 401 Authentication**
```bash
# Use test endpoints (no auth needed)
python test_ai_simple.py
```

### **Issue 3: 500 Internal Error**
```bash
# Check Django logs in terminal
# Look for Python tracebacks
# Common: ImportError, OperationalError
```

### **Issue 4: No Products Found**
```bash
# Add sample products via admin
python manage.py createsuperuser
# Go to http://localhost:8000/admin/
# Add some products
```

## 🎉 **Success Indicators**

- ✅ `python test_ai_simple.py` passes all tests
- ✅ AI responds with product links
- ✅ Frontend chatbox works
- ✅ Product search returns results
- ✅ No 500 errors in Django logs

## 📞 **Still Having Issues?**

1. **Share Django server logs** (copy Python tracebacks)
2. **Share test results:** `python test_ai_simple.py`
3. **Check database:** `python manage.py dbshell`
4. **Verify apps:** Check INSTALLED_APPS in settings.py

---

**Follow these steps in order and AI Chat will work! 🤖✨**

# 🧪 Frontend AI Chat Test Guide

## 🚀 Quick Test Steps

### 1. Start Servers
```bash
# Terminal 1: Start Django backend
python manage.py runserver

# Terminal 2: Start React frontend  
cd frontend
npm start
```

### 2. Test Backend First
```bash
# Quick backend test
python test_backend_simple.py
```

### 3. Frontend Testing

#### Option A: Use AI Chat Test Page (Recommended)
1. Go to: **http://localhost:3000/ai-chat-test**
2. Click **"Test Connection"** - should show "Connected"
3. **Login first** if you see "No auth token found"
4. Click **"Test All Messages"** to test multiple scenarios
5. Try custom messages in the input field

#### Option B: Use Main Chatbox
1. Go to: **http://localhost:3000**
2. **Login** with your credentials
3. Click the **floating robot icon** (bottom right)
4. Type messages and check responses

## 🔍 What to Check

### ✅ Success Indicators
- **Connection Status**: Shows "Connected" badge
- **Auth Status**: Shows "✅ Auth token found"
- **AI Responses**: Get meaningful replies like:
  - "Xin chào! Tôi là trợ lý AI..."
  - "Tôi có thể giúp bạn tìm sản phẩm..."
- **Quick Replies**: Buttons appear below AI messages
- **No Console Errors**: Check browser Developer Tools

### ❌ Error Indicators
- **500 Internal Server Error**: Backend issue
- **400 Bad Request**: Request format issue
- **401 Unauthorized**: Need to login
- **Connection Failed**: Backend not running
- **CORS Errors**: Configuration issue

## 🛠️ Troubleshooting

### Error: "Cannot connect to backend"
```bash
# Check if Django is running
curl http://localhost:8000/api/

# Start Django if not running
python manage.py runserver
```

### Error: "No auth token found"
1. Go to: http://localhost:3000/login
2. Login with your credentials
3. Check browser localStorage for 'authTokens'
4. Try AI chat again

### Error: "500 Internal Server Error"
```bash
# Check Django logs in terminal
# Look for Python errors/tracebacks

# Try simple backend test
python test_backend_simple.py
```

### Error: "session_id may not be null"
- This should be fixed in the latest code
- Refresh the page and try again

## 📱 Browser Testing

### Chrome/Edge
1. Open **Developer Tools** (F12)
2. Go to **Console** tab
3. Look for errors in red
4. Check **Network** tab for failed requests

### Firefox
1. Open **Web Developer Tools** (F12)
2. Check **Console** and **Network** tabs

## 🧪 Test Messages

Try these messages to test different features:

### Greeting
- "xin chào"
- "hello"
- "hi"

### Product Search
- "tìm áo màu xanh"
- "search for shoes"
- "sản phẩm giá rẻ"

### Size Help
- "size L có vừa không?"
- "hướng dẫn chọn size"
- "bảng size áo"

### Promotions
- "có khuyến mãi nào không?"
- "sale off"
- "giảm giá"

### Order Help
- "hướng dẫn đặt hàng"
- "cách thanh toán"
- "kiểm tra đơn hàng"

## 📊 Expected Responses

Each message should return:
```json
{
  "message": "AI response text",
  "session_id": "uuid-string",
  "message_type": "ai",
  "quick_replies": ["Button 1", "Button 2"],
  "actions_taken": [{"type": "greeting"}],
  "metadata": {"intent": "greeting"}
}
```

## 🔧 Debug Tools

### AI Chat Tester Component
- **Location**: http://localhost:3000/ai-chat-test
- **Features**:
  - Connection testing
  - Auth status check
  - Quick test buttons
  - Custom message input
  - Response history
  - Error logging

### Browser Console Commands
```javascript
// Check auth token
localStorage.getItem('authTokens')

// Test AI endpoint manually
fetch('http://localhost:8000/ai/chat/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'JWT ' + JSON.parse(localStorage.getItem('authTokens')).access
  },
  body: JSON.stringify({message: 'test'})
}).then(r => r.json()).then(console.log)
```

## 🎯 Success Criteria

✅ **AI Chat is working when:**
1. Backend connection test passes
2. Authentication token is present
3. AI chat returns meaningful responses
4. Quick reply buttons appear
5. No console errors
6. Session ID is maintained across messages

## 🆘 Still Having Issues?

1. **Clear browser cache** and refresh
2. **Logout and login again**
3. **Check Django server logs** for Python errors
4. **Try incognito/private browsing** mode
5. **Test with different browsers**

## 📞 Support

If you're still having issues:
1. Share screenshot of the test page results
2. Copy browser console errors
3. Share Django server logs
4. Mention which test steps failed

---

**Happy Testing! 🎉**

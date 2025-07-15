# Hướng dẫn Deploy AI Chatbox E-commerce

## 🚀 Tổng quan

Hệ thống AI Chatbox E-commerce bao gồm:
- **Backend**: Django REST API với AI chatbox
- **Frontend**: React.js với floating chatbox
- **Database**: PostgreSQL
- **Cache**: Redis
- **Web Server**: Nginx

## 📋 Yêu cầu hệ thống

- Docker & Docker Compose
- Git
- 2GB RAM tối thiểu
- 10GB dung lượng ổ cứng

## 🛠️ Cài đặt nhanh với Docker

### 1. Clone repository
```bash
git clone <your-repo-url>
cd Python-KienTap-
```

### 2. Cấu hình environment variables
```bash
cp .env.example .env
```

Chỉnh sửa file `.env` với thông tin của bạn:
```env
DEBUG=False
SECRET_KEY=your-very-secret-key-here
ALLOWED_HOSTS=your-domain.com,localhost
DATABASE_URL=postgresql://postgres:postgres123@db:5432/ecommerce_db
STRIPE_PUBLISHABLE_KEY=pk_test_your_key
STRIPE_SECRET_KEY=sk_test_your_key
```

### 3. Build và chạy containers
```bash
# Build images
docker-compose build

# Chạy services
docker-compose up -d

# Migrate database
docker-compose exec backend python manage.py migrate

# Tạo superuser
docker-compose exec backend python manage.py createsuperuser

# Setup AI knowledge base
docker-compose exec backend python manage.py setup_ai_knowledge

# Collect static files
docker-compose exec backend python manage.py collectstatic --noinput
```

### 4. Truy cập ứng dụng
- **Frontend**: http://localhost
- **Backend API**: http://localhost/api/
- **Admin**: http://localhost/admin/
- **AI Chat Admin**: http://localhost/admin/ai-chat/

## 🔧 Deploy thủ công (không dùng Docker)

### Backend Setup

1. **Cài đặt Python dependencies**
```bash
pip install -r requirements.txt
```

2. **Cấu hình database**
```bash
# PostgreSQL
sudo apt-get install postgresql postgresql-contrib
sudo -u postgres createdb ecommerce_db
```

3. **Migrate và setup**
```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py setup_ai_knowledge
python manage.py collectstatic
```

4. **Chạy server**
```bash
# Development
python manage.py runserver

# Production với Gunicorn
gunicorn --bind 0.0.0.0:8000 backend.wsgi:application
```

### Frontend Setup

1. **Cài đặt Node.js dependencies**
```bash
cd frontend
npm install
```

2. **Build production**
```bash
npm run build
```

3. **Serve với Nginx**
```bash
sudo cp nginx.conf /etc/nginx/sites-available/ecommerce
sudo ln -s /etc/nginx/sites-available/ecommerce /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## 🌐 Deploy lên VPS/Cloud

### 1. Chuẩn bị VPS
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 2. Deploy với Docker
```bash
# Clone code
git clone <your-repo-url>
cd Python-KienTap-

# Setup environment
cp .env.example .env
nano .env  # Chỉnh sửa với thông tin production

# Deploy
docker-compose -f docker-compose.yml up -d

# Setup database
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py createsuperuser
docker-compose exec backend python manage.py setup_ai_knowledge
```

### 3. Cấu hình domain và SSL
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

## 🔒 Bảo mật Production

### 1. Environment Variables
```env
DEBUG=False
SECRET_KEY=<generate-strong-secret-key>
ALLOWED_HOSTS=your-domain.com
SECURE_SSL_REDIRECT=True
SECURE_PROXY_SSL_HEADER=HTTP_X_FORWARDED_PROTO,https
```

### 2. Database Security
```bash
# Change default passwords
# Setup database backups
# Restrict database access
```

### 3. Firewall
```bash
sudo ufw enable
sudo ufw allow 22    # SSH
sudo ufw allow 80    # HTTP
sudo ufw allow 443   # HTTPS
```

## 📊 Monitoring và Logs

### 1. Xem logs
```bash
# All services
docker-compose logs

# Specific service
docker-compose logs backend
docker-compose logs frontend

# Follow logs
docker-compose logs -f backend
```

### 2. Health checks
```bash
# Check services status
docker-compose ps

# Check database connection
docker-compose exec backend python manage.py dbshell
```

## 🔄 Backup và Restore

### 1. Database Backup
```bash
# Backup
docker-compose exec db pg_dump -U postgres ecommerce_db > backup.sql

# Restore
docker-compose exec -T db psql -U postgres ecommerce_db < backup.sql
```

### 2. Media Files Backup
```bash
# Backup media files
tar -czf media_backup.tar.gz media/

# Restore
tar -xzf media_backup.tar.gz
```

## 🚀 Tối ưu Performance

### 1. Redis Caching
```python
# settings.py
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://redis:6379/1',
    }
}
```

### 2. Static Files với CDN
```python
# settings.py
STATIC_URL = 'https://your-cdn.com/static/'
```

### 3. Database Optimization
```bash
# PostgreSQL tuning
# Add indexes for frequently queried fields
# Use connection pooling
```

## 🤖 AI Chatbox Features

### 1. Tính năng chính
- ✅ Tìm kiếm sản phẩm thông minh
- ✅ Gợi ý size phù hợp
- ✅ Hỗ trợ đặt hàng
- ✅ FAQ tự động
- ✅ Admin dashboard

### 2. Cấu hình AI
```bash
# Setup knowledge base
docker-compose exec backend python manage.py setup_ai_knowledge

# Add custom knowledge via admin
# Access: http://your-domain.com/admin/ai-chat/
```

### 3. Tùy chỉnh responses
- Truy cập Admin AI Chat
- Thêm/sửa Knowledge Base
- Theo dõi chat statistics

## 🆘 Troubleshooting

### 1. Container không start
```bash
docker-compose logs <service-name>
docker-compose down && docker-compose up -d
```

### 2. Database connection error
```bash
# Check database status
docker-compose exec db pg_isready

# Reset database
docker-compose down -v
docker-compose up -d
```

### 3. Static files không load
```bash
docker-compose exec backend python manage.py collectstatic --noinput
```

### 4. AI chatbox không hoạt động
```bash
# Check backend logs
docker-compose logs backend

# Verify AI endpoints
curl http://localhost:8000/ai/chat/
```

## 📞 Hỗ trợ

Nếu gặp vấn đề trong quá trình deploy:
1. Kiểm tra logs chi tiết
2. Verify environment variables
3. Check network connectivity
4. Review firewall settings

---

**Chúc bạn deploy thành công! 🎉**

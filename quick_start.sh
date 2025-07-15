#!/bin/bash

# Quick Start Script for AI Chatbox E-commerce
echo "🚀 Starting AI Chatbox E-commerce deployment..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your configuration before continuing."
    echo "   Especially update SECRET_KEY, STRIPE keys, and ALLOWED_HOSTS"
    read -p "Press Enter to continue after editing .env file..."
fi

# Build and start containers
echo "🔨 Building Docker containers..."
docker-compose build

echo "🚀 Starting services..."
docker-compose up -d

# Wait for database to be ready
echo "⏳ Waiting for database to be ready..."
sleep 10

# Run migrations
echo "📊 Running database migrations..."
docker-compose exec -T backend python manage.py migrate

# Create superuser (optional)
echo "👤 Do you want to create a superuser? (y/n)"
read -r create_superuser
if [ "$create_superuser" = "y" ] || [ "$create_superuser" = "Y" ]; then
    docker-compose exec backend python manage.py createsuperuser
fi

# Setup AI knowledge base
echo "🤖 Setting up AI knowledge base..."
docker-compose exec -T backend python manage.py setup_ai_knowledge

# Collect static files
echo "📁 Collecting static files..."
docker-compose exec -T backend python manage.py collectstatic --noinput

# Show status
echo "📊 Checking services status..."
docker-compose ps

echo ""
echo "🎉 Deployment completed successfully!"
echo ""
echo "🌐 Access your application:"
echo "   Frontend: http://localhost"
echo "   Backend API: http://localhost/api/"
echo "   Django Admin: http://localhost/admin/"
echo "   AI Chat Admin: http://localhost/admin/ai-chat/"
echo ""
echo "🤖 AI Chatbox Features:"
echo "   ✅ Smart product search"
echo "   ✅ Size recommendations"
echo "   ✅ Order assistance"
echo "   ✅ FAQ automation"
echo "   ✅ Admin dashboard"
echo ""
echo "📖 For more information, see:"
echo "   - DEPLOYMENT.md for detailed deployment guide"
echo "   - AI_CHATBOX_README.md for AI features documentation"
echo ""
echo "🆘 If you encounter issues:"
echo "   - Check logs: docker-compose logs"
echo "   - Restart services: docker-compose restart"
echo "   - Full reset: docker-compose down -v && docker-compose up -d"
echo ""
echo "Happy chatting! 🎉"

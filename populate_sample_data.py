#!/usr/bin/env python3
"""
Populate sample data for testing AI Chat
"""

import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

def populate_sample_data():
    print("🔧 Populating sample data for AI Chat testing...")
    
    try:
        from api.models import Product, Brand, Category
        
        # Create sample brands
        print("\n1. Creating sample brands...")
        brands_data = [
            'Nike', 'Adidas', 'Zara', 'H&M', 'Uniqlo', 
            'Gucci', 'Puma', 'Converse', 'Vans', 'Supreme'
        ]
        
        for brand_name in brands_data:
            brand, created = Brand.objects.get_or_create(name=brand_name)
            if created:
                print(f"   ✅ Created brand: {brand_name}")
            else:
                print(f"   ⚠️ Brand exists: {brand_name}")
        
        # Create sample categories
        print("\n2. Creating sample categories...")
        categories_data = [
            'Áo thun', 'Áo polo', 'Áo khoác', 'Quần jean', 'Quần short',
            'Giày sneaker', 'Giày boot', 'Túi xách', 'Balo', 'Phụ kiện'
        ]
        
        for cat_name in categories_data:
            category, created = Category.objects.get_or_create(title=cat_name)
            if created:
                print(f"   ✅ Created category: {cat_name}")
            else:
                print(f"   ⚠️ Category exists: {cat_name}")
        
        # Create sample products
        print("\n3. Creating sample products...")
        
        # Get brands and categories
        nike = Brand.objects.get(name='Nike')
        adidas = Brand.objects.get(name='Adidas')
        zara = Brand.objects.get(name='Zara')
        
        ao_thun = Category.objects.get(title='Áo thun')
        quan_jean = Category.objects.get(title='Quần jean')
        giay_sneaker = Category.objects.get(title='Giày sneaker')
        
        products_data = [
            {
                'name': 'Áo thun Nike Dri-FIT màu đen',
                'description': 'Áo thun thể thao Nike Dri-FIT màu đen, chất liệu thoáng mát',
                'price': 250000,
                'brand': nike,
                'category': ao_thun,
                'image': 'products/nike_black_tshirt.jpg'
            },
            {
                'name': 'Áo thun Nike Essential màu trắng',
                'description': 'Áo thun Nike Essential màu trắng basic, phù hợp mọi hoàn cảnh',
                'price': 200000,
                'brand': nike,
                'category': ao_thun,
                'image': 'products/nike_white_tshirt.jpg'
            },
            {
                'name': 'Áo thun Adidas 3-Stripes màu xanh',
                'description': 'Áo thun Adidas 3-Stripes màu xanh navy, thiết kế iconic',
                'price': 280000,
                'brand': adidas,
                'category': ao_thun,
                'image': 'products/adidas_blue_tshirt.jpg'
            },
            {
                'name': 'Quần jean Zara Slim Fit màu đen',
                'description': 'Quần jean Zara Slim Fit màu đen, form dáng hiện đại',
                'price': 450000,
                'brand': zara,
                'category': quan_jean,
                'image': 'products/zara_black_jeans.jpg'
            },
            {
                'name': 'Quần jean Zara Regular màu xanh',
                'description': 'Quần jean Zara Regular màu xanh indigo classic',
                'price': 420000,
                'brand': zara,
                'category': quan_jean,
                'image': 'products/zara_blue_jeans.jpg'
            },
            {
                'name': 'Giày Nike Air Force 1 màu trắng',
                'description': 'Giày Nike Air Force 1 màu trắng classic, iconic design',
                'price': 850000,
                'brand': nike,
                'category': giay_sneaker,
                'image': 'products/nike_af1_white.jpg'
            },
            {
                'name': 'Giày Adidas Stan Smith màu trắng xanh',
                'description': 'Giày Adidas Stan Smith màu trắng với điểm nhấn xanh lá',
                'price': 750000,
                'brand': adidas,
                'category': giay_sneaker,
                'image': 'products/adidas_stansmith.jpg'
            },
            {
                'name': 'Áo polo Nike màu đỏ',
                'description': 'Áo polo Nike màu đỏ, phù hợp cho công sở và dạo phố',
                'price': 320000,
                'brand': nike,
                'category': ao_thun,
                'image': 'products/nike_red_polo.jpg'
            },
            {
                'name': 'Giày Nike React màu đen',
                'description': 'Giày Nike React màu đen, công nghệ đệm React tối ưu',
                'price': 950000,
                'brand': nike,
                'category': giay_sneaker,
                'image': 'products/nike_react_black.jpg'
            },
            {
                'name': 'Áo thun Zara Basic màu xám',
                'description': 'Áo thun Zara Basic màu xám, thiết kế tối giản',
                'price': 180000,
                'brand': zara,
                'category': ao_thun,
                'image': 'products/zara_grey_tshirt.jpg'
            }
        ]
        
        created_count = 0
        for product_data in products_data:
            product, created = Product.objects.get_or_create(
                name=product_data['name'],
                defaults=product_data
            )
            if created:
                created_count += 1
                print(f"   ✅ Created product: {product_data['name']}")
            else:
                print(f"   ⚠️ Product exists: {product_data['name']}")
        
        print(f"\n🎉 Sample data population completed!")
        print(f"   📊 Brands: {Brand.objects.count()}")
        print(f"   📊 Categories: {Category.objects.count()}")
        print(f"   📊 Products: {Product.objects.count()}")
        print(f"   📊 New products created: {created_count}")
        
        print(f"\n🧪 Test queries you can try:")
        print(f"   - 'tìm áo Nike màu đen'")
        print(f"   - 'giày Adidas dưới 800k'")
        print(f"   - 'quần jean Zara'")
        print(f"   - 'áo thun màu trắng'")
        print(f"   - 'sản phẩm Nike giá rẻ'")
        
        return True
        
    except Exception as e:
        print(f"❌ Error populating data: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return False

def check_existing_data():
    """Check existing data in database"""
    print("🔍 Checking existing data...")
    
    try:
        from api.models import Product, Brand, Category
        
        print(f"   📊 Brands: {Brand.objects.count()}")
        if Brand.objects.exists():
            brands = Brand.objects.all()[:5]
            print(f"      Sample: {[b.name for b in brands]}")
        
        print(f"   📊 Categories: {Category.objects.count()}")
        if Category.objects.exists():
            categories = Category.objects.all()[:5]
            print(f"      Sample: {[c.title for c in categories]}")
        
        print(f"   📊 Products: {Product.objects.count()}")
        if Product.objects.exists():
            products = Product.objects.all()[:3]
            for p in products:
                print(f"      - {p.name} ({p.price} VND)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error checking data: {e}")
        return False

if __name__ == "__main__":
    print("🚀 AI Chat Sample Data Setup")
    print("=" * 50)
    
    # Check existing data first
    if check_existing_data():
        print("\n" + "=" * 50)
        
        # Ask if user wants to populate more data
        if Product.objects.count() < 5:
            print("⚠️ Low product count detected. Populating sample data...")
            populate_sample_data()
        else:
            print("✅ Sufficient data exists. Ready for AI Chat testing!")
            
        print("\n🧪 Next steps:")
        print("1. Test backend: python test_database_integration.py")
        print("2. Test frontend: http://localhost:3000/ai-chat-test")
        print("3. Try complex queries with real data")
    else:
        print("❌ Cannot access database. Check Django setup.")
    
    print("=" * 50)

#!/usr/bin/env python
"""
Setup SubCategories và Size Guides cho Smart Chatbot
"""
import os
import sys
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from api.models import Category, SubCategory, Size, SizeGuide, Product

def setup_subcategories():
    """Tạo subcategories chi tiết"""
    print("🏗️ Setting up SubCategories...")
    
    # Lấy categories hiện tại
    print("📋 Available categories:")
    for cat in Category.objects.all():
        print(f"  - {cat.title}")

    # Tạo hoặc lấy parent categories
    ao_parent, created = Category.objects.get_or_create(
        title="Áo",
        defaults={
            'description': 'Tất cả các loại áo',
        }
    )
    if created:
        print(f"✅ Created parent category: {ao_parent.title}")

    quan_parent, created = Category.objects.get_or_create(
        title="Quần",
        defaults={
            'description': 'Tất cả các loại quần',
        }
    )
    if created:
        print(f"✅ Created parent category: {quan_parent.title}")

    print(f"✅ Using parent categories: {ao_parent.title}, {quan_parent.title}")
    
    # SubCategories cho Áo
    ao_subcategories = [
        {
            'title': 'Áo Thun',
            'description': 'Áo thun nam nữ, áo phông, áo thun oversize',
            'keywords': 'áo thun, áo phông, tshirt, t-shirt, áo thun nam, áo thun nữ, áo thun oversize, áo thun basic'
        },
        {
            'title': 'Áo Sơ Mi',
            'description': 'Áo sơ mi nam nữ, áo sơ mi công sở, áo sơ mi casual',
            'keywords': 'áo sơ mi, sơ mi, shirt, áo sơ mi nam, áo sơ mi nữ, áo sơ mi công sở, áo sơ mi tay dài, áo sơ mi tay ngắn'
        },
        {
            'title': 'Áo Khoác',
            'description': 'Áo khoác nam nữ, áo hoodie, áo cardigan',
            'keywords': 'áo khoác, hoodie, cardigan, jacket, áo khoác nam, áo khoác nữ, áo khoác dù, áo khoác jean'
        },
        {
            'title': 'Áo Polo',
            'description': 'Áo polo nam nữ, áo có cổ',
            'keywords': 'áo polo, polo, áo có cổ, áo polo nam, áo polo nữ'
        }
    ]
    
    # SubCategories cho Quần
    quan_subcategories = [
        {
            'title': 'Quần Jean',
            'description': 'Quần jean nam nữ, quần denim',
            'keywords': 'quần jean, jean, denim, quần jean nam, quần jean nữ, quần jean skinny, quần jean baggy, quần jean rách'
        },
        {
            'title': 'Quần Short',
            'description': 'Quần short nam nữ, quần ngắn',
            'keywords': 'quần short, quần ngắn, short, quần short nam, quần short nữ, quần short jean, quần short kaki'
        },
        {
            'title': 'Quần Dài',
            'description': 'Quần dài nam nữ, quần âu, quần kaki',
            'keywords': 'quần dài, quần âu, quần kaki, quần dài nam, quần dài nữ, quần công sở'
        },
        {
            'title': 'Quần Jogger',
            'description': 'Quần jogger, quần thể thao',
            'keywords': 'quần jogger, jogger, quần thể thao, quần jogger nam, quần jogger nữ'
        }
    ]
    
    # Tạo subcategories cho Áo
    for sub_data in ao_subcategories:
        subcategory, created = SubCategory.objects.get_or_create(
            category=ao_parent,
            title=sub_data['title'],
            defaults={
                'description': sub_data['description'],
                'keywords': sub_data['keywords']
            }
        )
        if created:
            print(f"✅ Created: {subcategory}")
        else:
            print(f"📝 Updated: {subcategory}")
            subcategory.description = sub_data['description']
            subcategory.keywords = sub_data['keywords']
            subcategory.save()

    # Tạo subcategories cho Quần
    for sub_data in quan_subcategories:
        subcategory, created = SubCategory.objects.get_or_create(
            category=quan_parent,
            title=sub_data['title'],
            defaults={
                'description': sub_data['description'],
                'keywords': sub_data['keywords']
            }
        )
        if created:
            print(f"✅ Created: {subcategory}")
        else:
            print(f"📝 Updated: {subcategory}")
            subcategory.description = sub_data['description']
            subcategory.keywords = sub_data['keywords']
            subcategory.save()

def setup_size_guides():
    """Tạo size guides cho subcategories"""
    print("\n📏 Setting up Size Guides...")
    
    # Lấy sizes
    sizes = Size.objects.all().order_by('order')
    if not sizes.exists():
        print("❌ Không có Size nào trong database!")
        return
    
    # Size guide cho Áo Thun
    try:
        ao_thun = SubCategory.objects.get(title="Áo Thun")
        size_guides_ao_thun = [
            {'size': 'S', 'height_min': 150, 'height_max': 160, 'weight_min': 45, 'weight_max': 55, 'chest': '88-92', 'notes': 'Form vừa'},
            {'size': 'M', 'height_min': 160, 'height_max': 170, 'weight_min': 55, 'weight_max': 65, 'chest': '92-96', 'notes': 'Form vừa'},
            {'size': 'L', 'height_min': 170, 'height_max': 175, 'weight_min': 65, 'weight_max': 75, 'chest': '96-100', 'notes': 'Form vừa'},
            {'size': 'XL', 'height_min': 175, 'height_max': 180, 'weight_min': 75, 'weight_max': 85, 'chest': '100-104', 'notes': 'Form vừa'},
        ]
        
        for guide_data in size_guides_ao_thun:
            try:
                size_obj = Size.objects.get(name=guide_data['size'])
                guide, created = SizeGuide.objects.get_or_create(
                    subcategory=ao_thun,
                    size=size_obj,
                    defaults={
                        'height_min': guide_data['height_min'],
                        'height_max': guide_data['height_max'],
                        'weight_min': guide_data['weight_min'],
                        'weight_max': guide_data['weight_max'],
                        'chest': guide_data['chest'],
                        'notes': guide_data['notes']
                    }
                )
                if created:
                    print(f"✅ Created size guide: {guide}")
            except Size.DoesNotExist:
                print(f"❌ Size {guide_data['size']} không tồn tại")
                
    except SubCategory.DoesNotExist:
        print("❌ SubCategory 'Áo Thun' không tồn tại")

def assign_products_to_subcategories():
    """Gán products hiện tại vào subcategories"""
    print("\n🏷️ Assigning products to subcategories...")
    
    # Gán áo thun
    try:
        ao_thun_subcat = SubCategory.objects.get(title="Áo Thun")
        ao_thun_products = Product.objects.filter(
            category__title__icontains="áo",
            name__icontains="thun"
        )
        
        for product in ao_thun_products:
            product.subcategory = ao_thun_subcat
            product.save()
            print(f"✅ Assigned '{product.name}' to Áo Thun")
            
    except SubCategory.DoesNotExist:
        print("❌ SubCategory 'Áo Thun' không tồn tại")
    
    # Gán áo sơ mi
    try:
        ao_so_mi_subcat = SubCategory.objects.get(title="Áo Sơ Mi")
        ao_so_mi_products = Product.objects.filter(
            category__title__icontains="áo",
            name__icontains="sơ mi"
        )
        
        for product in ao_so_mi_products:
            product.subcategory = ao_so_mi_subcat
            product.save()
            print(f"✅ Assigned '{product.name}' to Áo Sơ Mi")
            
    except SubCategory.DoesNotExist:
        print("❌ SubCategory 'Áo Sơ Mi' không tồn tại")

def main():
    """Main function"""
    print("🚀 Starting SubCategory Setup...")
    
    setup_subcategories()
    setup_size_guides()
    assign_products_to_subcategories()
    
    print("\n✅ SubCategory setup completed!")
    
    # Show results
    print("\n📊 Results:")
    print(f"SubCategories: {SubCategory.objects.count()}")
    print(f"Size Guides: {SizeGuide.objects.count()}")
    print(f"Products with SubCategory: {Product.objects.filter(subcategory__isnull=False).count()}")

if __name__ == "__main__":
    main()

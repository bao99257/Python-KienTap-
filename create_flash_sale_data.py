#!/usr/bin/env python
"""
Script to create sample Flash Sale data for testing
Run this script from the Django project root directory
"""

import os
import sys
import django
from datetime import datetime, timedelta
from django.utils import timezone

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth.models import User
from api.models import FlashSaleProgram, FlashSaleItem, Product

def create_sample_flash_sale_data():
    """Create sample Flash Sale programs and items"""

    # Get or create admin user
    admin_user, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@example.com',
            'is_staff': True,
            'is_superuser': True
        }
    )
    if created:
        admin_user.set_password('admin123')
        admin_user.save()
        print("Created admin user: admin/admin123")

    # Get some products for Flash Sale
    products = Product.objects.all()
    if not products:
        print("No products found. Please create some products first.")
        return

    print(f"Found {len(products)} products to use in Flash Sale")

    # Create Flash Sale programs for today - every 3 hours
    now = timezone.now()
    today = now.date()

    # Define time slots: 00-03, 03-06, 06-09, 09-12, 12-15, 15-18, 18-21, 21-24
    time_slots = [
        (0, "FLASH SALE ĐÊM KHUYA - Giá Sốc 0h"),
        (3, "FLASH SALE BÌNH MINH - Deal Khủng 3h"),
        (6, "FLASH SALE SÁNG SỚM - Ưu Đãi 6h"),
        (9, "FLASH SALE SÁNG - Siêu Rẻ 9h"),
        (12, "FLASH SALE TRƯA - Nóng Bỏng 12h"),
        (15, "FLASH SALE CHIỀU - Bùng Nổ 15h"),
        (18, "FLASH SALE TỐI - Săn Sale 18h"),
        (21, "FLASH SALE ĐÊM - Cực Shock 21h")
    ]

    print(f"Creating {len(time_slots)} Flash Sale programs for today...")

    created_programs = []
    
    # Create programs for each time slot
    for slot_hour, slot_name in time_slots:
        program_start = timezone.make_aware(datetime.combine(today, datetime.min.time().replace(hour=slot_hour, minute=0)))
        program_end = program_start + timedelta(hours=3)

        # Determine status based on current time
        current_hour = now.hour
        if slot_hour <= current_hour < slot_hour + 3:
            status = 'active'
            description = f'Đang diễn ra! {slot_name} với nhiều ưu đãi hấp dẫn'
        elif slot_hour > current_hour:
            status = 'upcoming'
            description = f'Sắp diễn ra! {slot_name} với giá shock'
        else:
            status = 'ended'
            description = f'Đã kết thúc! {slot_name}'

        program, created = FlashSaleProgram.objects.get_or_create(
            name=slot_name,
            defaults={
                'description': description,
                'start_time': program_start,
                'end_time': program_end,
                'status': status,
                'is_active': True,
                'created_by': admin_user
            }
        )

        if created:
            print(f"Created Flash Sale program: {program.name}")
            created_programs.append(program)

            # Add products to this program
            # Distribute products across different time slots
            products_for_slot = products[slot_hour % len(products):(slot_hour % len(products)) + 3] if len(products) >= 3 else products

            for i, product in enumerate(products_for_slot):
                original_price = float(product.price) if product.price else 100000

                # Different discount rates for different time slots
                discount_rates = {
                    0: 0.6,   # 40% discount for midnight
                    3: 0.7,   # 30% discount for early morning
                    6: 0.5,   # 50% discount for morning
                    9: 0.4,   # 60% discount for late morning
                    12: 0.3,  # 70% discount for lunch
                    15: 0.5,  # 50% discount for afternoon
                    18: 0.2,  # 80% discount for evening
                    21: 0.4   # 60% discount for night
                }

                flash_price = original_price * discount_rates.get(slot_hour, 0.5)

                # Set sold quantity based on status
                if status == 'ended':
                    sold_qty = 15 + (i * 5)  # Already sold some
                elif status == 'active':
                    sold_qty = 5 + (i * 2)   # Currently selling
                else:
                    sold_qty = 0             # Not started yet

                FlashSaleItem.objects.get_or_create(
                    program=program,
                    product=product,
                    defaults={
                        'original_price': original_price,
                        'flash_price': flash_price,
                        'total_quantity': 50 + (i * 10),
                        'sold_quantity': sold_qty,
                        'max_per_user': 2 if slot_hour in [12, 18] else 1,  # Higher limit for peak hours
                        'is_active': True
                    }
                )

            print(f"Added {len(products_for_slot)} items to {program.name}")
        else:
            print(f"Program already exists: {program.name}")
    
    print(f"\n✅ Flash Sale data created successfully!")
    print(f"Created {len(created_programs)} new programs")
    print("\nAll Flash Sale programs for today:")
    for program in FlashSaleProgram.objects.filter(start_time__date=today).order_by('start_time'):
        print(f"- {program.name}: {program.start_time.strftime('%H:%M')} - {program.end_time.strftime('%H:%M')} ({program.status})")
        print(f"  Items: {program.items.count()}")

    print(f"\nTotal Flash Sale programs: {FlashSaleProgram.objects.count()}")
    print(f"Total Flash Sale items: {FlashSaleItem.objects.count()}")

    # Show current time and active program
    print(f"\nCurrent time: {now.strftime('%H:%M')}")
    active_program = FlashSaleProgram.objects.filter(
        start_time__lte=now,
        end_time__gte=now,
        is_active=True
    ).first()
    if active_program:
        print(f"Currently active: {active_program.name}")
    else:
        print("No active Flash Sale program right now")

if __name__ == '__main__':
    create_sample_flash_sale_data()

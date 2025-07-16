#!/usr/bin/env python
"""
Debug outside range logic
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from ai_chat.size_consultant import size_consultant

def debug_outside_range():
    """Debug outside range detection"""
    
    print("🔍 DEBUG OUTSIDE RANGE DETECTION")
    print("=" * 50)
    
    test_cases = [
        (156, 89, 'ao'),   # User case
        (156, 90, 'ao'),   # User case
        (150, 100, 'ao'),  # Extreme case
        (200, 50, 'ao'),   # Extreme case
        (165, 60, 'ao'),   # Normal case
    ]
    
    for height, weight, product_type in test_cases:
        print(f"\nTest: {height}cm, {weight}kg, {product_type}")
        
        # Test outside range detection
        is_outside = size_consultant._is_outside_normal_range(height, weight, product_type)
        print(f"  Is outside range: {is_outside}")
        
        # Test full recommendation
        measurements = {'height': height, 'weight': weight, 'gender': 'unisex'}
        result = size_consultant.recommend_size(measurements, product_type)
        print(f"  Success: {result['success']}")
        print(f"  Special case: {result.get('special_case', False)}")
        if result['success']:
            sizes = [s['size'] for s in result['recommended_sizes']]
            print(f"  Recommended sizes: {sizes}")
        else:
            print(f"  Message: {result['message'][:100]}...")
    
    # Check size chart ranges
    print(f"\n📊 SIZE CHART RANGES:")
    chart = size_consultant.SIZE_CHART['ao']
    for size, data in chart.items():
        if 'nam' in data:
            nam_data = data['nam']
            print(f"  {size} Nam: {nam_data['cao']}, {nam_data['can']}")
        if 'nu' in data:
            nu_data = data['nu']
            print(f"  {size} Nữ: {nu_data['cao']}, {nu_data['can']}")

if __name__ == "__main__":
    debug_outside_range()

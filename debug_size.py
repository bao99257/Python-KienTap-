#!/usr/bin/env python
"""
Debug size consultation
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from ai_chat.size_consultant import size_consultant

def debug_size():
    """Debug size consultation"""
    
    print("🔍 DEBUG SIZE CONSULTATION")
    print("=" * 50)
    
    # Test case: 1m56, 59kg
    measurements = {'height': 156, 'weight': 59, 'gender': 'unisex'}
    product_type = 'ao'
    
    print(f"Measurements: {measurements}")
    print(f"Product type: {product_type}")
    print()
    
    # Test recommend_size
    result = size_consultant.recommend_size(measurements, product_type)
    print(f"Recommend result: {result}")
    print()
    
    # Test _find_closest_size directly
    closest = size_consultant._find_closest_size(156, 59, 'ao', 'unisex')
    print(f"Closest size: {closest}")
    print()
    
    # Check size chart
    chart = size_consultant.SIZE_CHART['ao']
    print("Size chart for 'ao':")
    for size, data in chart.items():
        if 'nam' in data:
            nam_data = data['nam']
            print(f"  {size}: Nam {nam_data['cao']}, {nam_data['can']}")
        if 'nu' in data:
            nu_data = data['nu']
            print(f"  {size}: Nữ {nu_data['cao']}, {nu_data['can']}")
    print()
    
    # Test with different measurements
    test_cases = [
        {'height': 156, 'weight': 59, 'gender': 'unisex'},
        {'height': 156, 'weight': 59, 'gender': 'nu'},
        {'height': 165, 'weight': 56, 'gender': 'unisex'},
        {'height': 165, 'weight': 56, 'gender': 'nu'},
    ]
    
    for measurements in test_cases:
        result = size_consultant.recommend_size(measurements, 'ao')
        print(f"Test {measurements}: {result.get('success')} - {result.get('recommended_sizes', [])}")

if __name__ == "__main__":
    debug_size()

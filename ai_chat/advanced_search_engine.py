"""
Advanced Product Search Engine with AI-powered filtering and recommendations
"""

import re
import logging
from typing import Dict, List, Optional, Tuple, Any
from django.db.models import Q, Count, Avg, F, Case, When, IntegerField
from django.contrib.auth.models import User
from dataclasses import dataclass
from enum import Enum

from products.models import Product, Category, Brand
from orders.models import Order, OrderItem

logger = logging.getLogger(__name__)

class SortOption(Enum):
    RELEVANCE = "relevance"
    PRICE_LOW = "price_low"
    PRICE_HIGH = "price_high"
    NEWEST = "newest"
    POPULAR = "popular"
    RATING = "rating"

@dataclass
class SearchFilter:
    """Bộ lọc tìm kiếm nâng cao"""
    categories: List[str] = None
    brands: List[str] = None
    price_min: Optional[int] = None
    price_max: Optional[int] = None
    sizes: List[str] = None
    colors: List[str] = None
    in_stock_only: bool = True
    on_sale_only: bool = False
    min_rating: Optional[float] = None
    sort_by: SortOption = SortOption.RELEVANCE

@dataclass
class SearchResult:
    """Kết quả tìm kiếm"""
    products: List[Dict]
    total_count: int
    filters_applied: Dict[str, Any]
    suggestions: List[str]
    related_searches: List[str]
    facets: Dict[str, List[Dict]]  # For filtering UI

class AdvancedSearchEngine:
    """Search engine nâng cao với AI-powered features"""
    
    def __init__(self):
        self.price_ranges = self._build_price_ranges()
        self.search_synonyms = self._build_search_synonyms()
        self.trending_cache_timeout = 3600  # 1 hour
        
    def _build_price_ranges(self) -> Dict[str, Tuple[int, int]]:
        """Định nghĩa các khoảng giá phổ biến"""
        return {
            'rẻ': (0, 200000),
            'bình dân': (200000, 500000),
            'trung bình': (500000, 1000000),
            'cao cấp': (1000000, 2000000),
            'luxury': (2000000, float('inf')),
            'dưới 100k': (0, 100000),
            'dưới 200k': (0, 200000),
            'dưới 500k': (0, 500000),
            'trên 1tr': (1000000, float('inf')),
        }
    
    def _build_search_synonyms(self) -> Dict[str, List[str]]:
        """Từ đồng nghĩa cho tìm kiếm"""
        return {
            'áo thun': ['t-shirt', 'tshirt', 'áo phông', 'áo cotton'],
            'áo sơ mi': ['shirt', 'áo công sở', 'áo dài tay'],
            'quần jean': ['jeans', 'quần bò', 'denim'],
            'giày thể thao': ['sneaker', 'giày chạy bộ', 'giày tập'],
            'váy': ['dress', 'đầm', 'chân váy'],
            'đen': ['black', 'màu đen'],
            'trắng': ['white', 'màu trắng'],
            'xanh': ['blue', 'navy', 'xanh dương'],
        }
    
    def search_products(self, query: str, filters: SearchFilter = None, 
                       user: User = None, page: int = 1, per_page: int = 20) -> SearchResult:
        """Tìm kiếm sản phẩm nâng cao"""
        
        if filters is None:
            filters = SearchFilter()
        
        # Parse query để extract filters
        parsed_query, extracted_filters = self._parse_search_query(query)
        
        # Merge extracted filters với filters được truyền vào
        merged_filters = self._merge_filters(filters, extracted_filters)
        
        # Build Django query
        queryset = self._build_queryset(parsed_query, merged_filters, user)
        
        # Apply sorting
        queryset = self._apply_sorting(queryset, merged_filters.sort_by, parsed_query)
        
        # Get total count before pagination
        total_count = queryset.count()
        
        # Apply pagination
        start = (page - 1) * per_page
        end = start + per_page
        products_queryset = queryset[start:end]
        
        # Convert to dict format
        products = self._format_products(products_queryset, parsed_query)
        
        # Generate suggestions and related searches
        suggestions = self._generate_suggestions(parsed_query, merged_filters, total_count)
        related_searches = self._generate_related_searches(parsed_query)
        
        # Generate facets for filtering UI
        facets = self._generate_facets(parsed_query, merged_filters)
        
        return SearchResult(
            products=products,
            total_count=total_count,
            filters_applied=self._serialize_filters(merged_filters),
            suggestions=suggestions,
            related_searches=related_searches,
            facets=facets
        )
    
    def _parse_search_query(self, query: str) -> Tuple[str, SearchFilter]:
        """Parse query để extract filters tự động"""
        filters = SearchFilter()
        cleaned_query = query.lower().strip()
        
        # Extract price range
        for price_term, (min_price, max_price) in self.price_ranges.items():
            if price_term in cleaned_query:
                filters.price_min = min_price
                filters.price_max = max_price if max_price != float('inf') else None
                cleaned_query = cleaned_query.replace(price_term, '').strip()
                break
        
        # Extract specific price mentions
        price_patterns = [
            r'dưới (\d+)k',
            r'under (\d+)k',
            r'từ (\d+)k đến (\d+)k',
            r'(\d+)k - (\d+)k'
        ]
        
        for pattern in price_patterns:
            match = re.search(pattern, cleaned_query)
            if match:
                if len(match.groups()) == 1:  # "dưới Xk"
                    filters.price_max = int(match.group(1)) * 1000
                elif len(match.groups()) == 2:  # "từ Xk đến Yk"
                    filters.price_min = int(match.group(1)) * 1000
                    filters.price_max = int(match.group(2)) * 1000
                cleaned_query = re.sub(pattern, '', cleaned_query).strip()
                break
        
        # Extract sizes
        size_pattern = r'\b(S|M|L|XL|XXL|28|29|30|31|32|33|34|35|36|37|38|39|40|41|42)\b'
        size_matches = re.findall(size_pattern, cleaned_query, re.IGNORECASE)
        if size_matches:
            filters.sizes = list(set(size_matches))
            cleaned_query = re.sub(size_pattern, '', cleaned_query, flags=re.IGNORECASE).strip()
        
        # Extract colors
        color_keywords = ['đen', 'trắng', 'xanh', 'đỏ', 'vàng', 'tím', 'hồng', 'nâu', 'xám', 'be']
        found_colors = []
        for color in color_keywords:
            if color in cleaned_query:
                found_colors.append(color)
                cleaned_query = cleaned_query.replace(color, '').strip()
        
        if found_colors:
            filters.colors = found_colors
        
        # Extract brands (if mentioned)
        brand_keywords = ['nike', 'adidas', 'gucci', 'zara', 'h&m', 'uniqlo']
        found_brands = []
        for brand in brand_keywords:
            if brand in cleaned_query:
                found_brands.append(brand)
                cleaned_query = cleaned_query.replace(brand, '').strip()
        
        if found_brands:
            filters.brands = found_brands
        
        # Check for sale/promotion keywords
        sale_keywords = ['giảm giá', 'khuyến mãi', 'sale', 'promotion', 'discount']
        if any(keyword in cleaned_query for keyword in sale_keywords):
            filters.on_sale_only = True
            for keyword in sale_keywords:
                cleaned_query = cleaned_query.replace(keyword, '').strip()
        
        # Clean up query
        cleaned_query = re.sub(r'\s+', ' ', cleaned_query).strip()
        
        return cleaned_query, filters
    
    def _merge_filters(self, base_filters: SearchFilter, extracted_filters: SearchFilter) -> SearchFilter:
        """Merge filters từ query parsing với filters được truyền vào"""
        merged = SearchFilter()
        
        # Merge từng field
        merged.categories = base_filters.categories or extracted_filters.categories
        merged.brands = base_filters.brands or extracted_filters.brands
        merged.price_min = base_filters.price_min or extracted_filters.price_min
        merged.price_max = base_filters.price_max or extracted_filters.price_max
        merged.sizes = base_filters.sizes or extracted_filters.sizes
        merged.colors = base_filters.colors or extracted_filters.colors
        merged.in_stock_only = base_filters.in_stock_only
        merged.on_sale_only = base_filters.on_sale_only or extracted_filters.on_sale_only
        merged.min_rating = base_filters.min_rating or extracted_filters.min_rating
        merged.sort_by = base_filters.sort_by
        
        return merged
    
    def _build_queryset(self, query: str, filters: SearchFilter, user: User = None):
        """Build Django queryset với filters"""
        queryset = Product.objects.select_related('category', 'brand').prefetch_related('images')
        
        # Text search với synonyms
        if query:
            search_terms = [query]
            
            # Add synonyms
            for term, synonyms in self.search_synonyms.items():
                if term in query:
                    search_terms.extend(synonyms)
            
            # Build Q object for text search
            text_query = Q()
            for term in search_terms:
                text_query |= (
                    Q(name__icontains=term) |
                    Q(description__icontains=term) |
                    Q(category__name__icontains=term) |
                    Q(brand__name__icontains=term)
                )
            
            queryset = queryset.filter(text_query)
        
        # Apply filters
        if filters.categories:
            queryset = queryset.filter(category__name__in=filters.categories)
        
        if filters.brands:
            queryset = queryset.filter(brand__name__in=filters.brands)
        
        if filters.price_min is not None:
            queryset = queryset.filter(price__gte=filters.price_min)
        
        if filters.price_max is not None:
            queryset = queryset.filter(price__lte=filters.price_max)
        
        if filters.sizes:
            # Assuming sizes are stored in a related model or JSON field
            queryset = queryset.filter(sizes__overlap=filters.sizes)
        
        if filters.colors:
            queryset = queryset.filter(color__in=filters.colors)
        
        if filters.in_stock_only:
            queryset = queryset.filter(stock__gt=0)
        
        if filters.on_sale_only:
            queryset = queryset.filter(sale_price__isnull=False)
        
        if filters.min_rating:
            queryset = queryset.filter(rating__gte=filters.min_rating)
        
        return queryset.distinct()
    
    def _apply_sorting(self, queryset, sort_by: SortOption, query: str = ""):
        """Apply sorting to queryset"""
        if sort_by == SortOption.PRICE_LOW:
            return queryset.order_by('price')
        elif sort_by == SortOption.PRICE_HIGH:
            return queryset.order_by('-price')
        elif sort_by == SortOption.NEWEST:
            return queryset.order_by('-created_at')
        elif sort_by == SortOption.POPULAR:
            # Sort by order count
            return queryset.annotate(
                order_count=Count('orderitem')
            ).order_by('-order_count')
        elif sort_by == SortOption.RATING:
            return queryset.order_by('-rating')
        else:  # RELEVANCE
            if query:
                # Simple relevance scoring
                return queryset.annotate(
                    relevance_score=Case(
                        When(name__icontains=query, then=3),
                        When(category__name__icontains=query, then=2),
                        When(description__icontains=query, then=1),
                        default=0,
                        output_field=IntegerField()
                    )
                ).order_by('-relevance_score', '-created_at')
            else:
                return queryset.order_by('-created_at')
    
    def _format_products(self, products_queryset, query: str = "") -> List[Dict]:
        """Format products cho response"""
        products = []
        
        for product in products_queryset:
            # Get primary image
            primary_image = product.images.first()
            image_url = primary_image.image.url if primary_image else '/static/images/placeholder.png'
            
            # Calculate discount percentage
            discount_percent = 0
            if product.sale_price and product.price > product.sale_price:
                discount_percent = int((product.price - product.sale_price) / product.price * 100)
            
            products.append({
                'id': product.id,
                'name': product.name,
                'price': float(product.price),
                'sale_price': float(product.sale_price) if product.sale_price else None,
                'discount_percent': discount_percent,
                'image': image_url,
                'category': product.category.name,
                'brand': product.brand.name if product.brand else '',
                'rating': float(product.rating) if product.rating else 0,
                'stock': product.stock,
                'is_new': (timezone.now() - product.created_at).days <= 30,
                'url': f'/products/{product.id}/',
                'short_description': product.description[:100] + '...' if len(product.description) > 100 else product.description
            })
        
        return products
    
    def _generate_suggestions(self, query: str, filters: SearchFilter, result_count: int) -> List[str]:
        """Generate search suggestions"""
        suggestions = []
        
        if result_count == 0:
            suggestions.extend([
                'Thử tìm với từ khóa khác',
                'Bỏ bớt bộ lọc',
                'Xem tất cả sản phẩm',
                'Liên hệ tư vấn'
            ])
        elif result_count < 5:
            suggestions.extend([
                'Xem sản phẩm tương tự',
                'Mở rộng tìm kiếm',
                'Thay đổi khoảng giá'
            ])
        else:
            suggestions.extend([
                'Lọc theo giá',
                'Lọc theo thương hiệu',
                'Sắp xếp theo giá',
                'Xem sản phẩm mới nhất'
            ])
        
        return suggestions[:4]
    
    def _generate_related_searches(self, query: str) -> List[str]:
        """Generate related search terms"""
        related = []
        
        # Based on query content
        if 'áo' in query:
            related.extend(['áo thun nam', 'áo sơ mi', 'áo khoác'])
        elif 'quần' in query:
            related.extend(['quần jean', 'quần kaki', 'quần short'])
        elif 'giày' in query:
            related.extend(['giày thể thao', 'giày cao gót', 'giày da'])
        
        # Add trending searches
        related.extend(['sản phẩm hot', 'khuyến mãi', 'hàng mới về'])
        
        return related[:5]
    
    def _generate_facets(self, query: str, filters: SearchFilter) -> Dict[str, List[Dict]]:
        """Generate facets for filtering UI"""
        # This would typically query the database for available filter options
        return {
            'categories': [
                {'name': 'Áo thun', 'count': 45},
                {'name': 'Quần jean', 'count': 32},
                {'name': 'Giày thể thao', 'count': 28}
            ],
            'brands': [
                {'name': 'Nike', 'count': 15},
                {'name': 'Adidas', 'count': 12},
                {'name': 'Zara', 'count': 8}
            ],
            'price_ranges': [
                {'range': '0-200k', 'count': 25},
                {'range': '200k-500k', 'count': 35},
                {'range': '500k-1tr', 'count': 20}
            ]
        }
    
    def _serialize_filters(self, filters: SearchFilter) -> Dict[str, Any]:
        """Serialize filters for response"""
        return {
            'categories': filters.categories,
            'brands': filters.brands,
            'price_min': filters.price_min,
            'price_max': filters.price_max,
            'sizes': filters.sizes,
            'colors': filters.colors,
            'in_stock_only': filters.in_stock_only,
            'on_sale_only': filters.on_sale_only,
            'min_rating': filters.min_rating,
            'sort_by': filters.sort_by.value
        }

# Global instance
advanced_search_engine = AdvancedSearchEngine()

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from django.utils import timezone
from django.db.models import Q, F
from django.shortcuts import get_object_or_404
from datetime import datetime, timedelta

from api.models import FlashSaleProgram, FlashSaleItem, FlashSalePurchase, FlashSaleTimeSlot, Product
from api.serializers import (
    FlashSaleProgramSerializer, FlashSaleItemSerializer, 
    FlashSalePurchaseSerializer, FlashSaleTimeSlotSerializer
)


class FlashSaleProgramViewSet(ModelViewSet):
    """ViewSet cho Flash Sale Programs"""
    queryset = FlashSaleProgram.objects.all()
    serializer_class = FlashSaleProgramSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        queryset = FlashSaleProgram.objects.all()
        
        # Filter by status
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by active programs
        is_active = self.request.query_params.get('is_active', None)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        return queryset.order_by('-start_time')
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=False, methods=['get'])
    def current(self, request):
        """Lấy chương trình Flash Sale hiện tại"""
        now = timezone.now()
        current_program = FlashSaleProgram.objects.filter(
            start_time__lte=now,
            end_time__gte=now,
            is_active=True
        ).first()
        
        if current_program:
            serializer = self.get_serializer(current_program)
            return Response(serializer.data)
        
        return Response({'message': 'Không có chương trình Flash Sale nào đang diễn ra'}, 
                       status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Lấy chương trình Flash Sale sắp tới"""
        now = timezone.now()
        upcoming_programs = FlashSaleProgram.objects.filter(
            start_time__gt=now,
            is_active=True
        ).order_by('start_time')[:5]
        
        serializer = self.get_serializer(upcoming_programs, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def today_timeline(self, request):
        """Lấy timeline Flash Sale trong ngày"""
        today = timezone.now().date()
        start_of_day = timezone.make_aware(datetime.combine(today, datetime.min.time()))
        end_of_day = timezone.make_aware(datetime.combine(today, datetime.max.time()))
        
        programs = FlashSaleProgram.objects.filter(
            start_time__gte=start_of_day,
            start_time__lte=end_of_day,
            is_active=True
        ).order_by('start_time')
        
        serializer = self.get_serializer(programs, many=True)
        return Response(serializer.data)


class FlashSaleItemViewSet(ModelViewSet):
    """ViewSet cho Flash Sale Items"""
    queryset = FlashSaleItem.objects.all()
    serializer_class = FlashSaleItemSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        queryset = FlashSaleItem.objects.select_related('product', 'program').all()
        
        # Filter by program
        program_id = self.request.query_params.get('program', None)
        if program_id:
            queryset = queryset.filter(program_id=program_id)
        
        # Filter by category
        category = self.request.query_params.get('category', None)
        if category:
            queryset = queryset.filter(product__category__title__icontains=category)
        
        # Filter by available items only
        available_only = self.request.query_params.get('available_only', None)
        if available_only and available_only.lower() == 'true':
            queryset = queryset.filter(
                is_active=True,
                program__is_active=True,
                program__start_time__lte=timezone.now(),
                program__end_time__gte=timezone.now()
            ).annotate(
                remaining=F('total_quantity') - F('sold_quantity')
            ).filter(remaining__gt=0)
        
        return queryset.order_by('-created_at')
    
    @action(detail=False, methods=['get'])
    def current_sale(self, request):
        """Lấy sản phẩm Flash Sale hiện tại"""
        now = timezone.now()
        current_items = FlashSaleItem.objects.filter(
            program__start_time__lte=now,
            program__end_time__gte=now,
            program__is_active=True,
            is_active=True
        ).select_related('product', 'program').annotate(
            remaining=F('total_quantity') - F('sold_quantity')
        ).filter(remaining__gt=0)
        
        # Filter by category if provided
        category = request.query_params.get('category', None)
        if category:
            current_items = current_items.filter(product__category__title__icontains=category)
        
        serializer = self.get_serializer(current_items, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def check_purchase(self, request, pk=None):
        """Kiểm tra khả năng mua sản phẩm"""
        if not request.user.is_authenticated:
            return Response({'error': 'Vui lòng đăng nhập'}, status=status.HTTP_401_UNAUTHORIZED)
        
        item = self.get_object()
        quantity = int(request.data.get('quantity', 1))
        
        can_purchase, message = item.can_purchase(request.user, quantity)
        
        return Response({
            'can_purchase': can_purchase,
            'message': message,
            'remaining_quantity': item.remaining_quantity,
            'user_purchased': FlashSalePurchase.objects.filter(
                item=item, user=request.user
            ).aggregate(total=models.Sum('quantity'))['total'] or 0
        })


@api_view(['GET'])
@permission_classes([IsAuthenticatedOrReadOnly])
def flash_sale_dashboard(request):
    """Dashboard tổng quan Flash Sale"""
    now = timezone.now()
    
    # Current program
    current_program = FlashSaleProgram.objects.filter(
        start_time__lte=now,
        end_time__gte=now,
        is_active=True
    ).first()
    
    # Next program
    next_program = FlashSaleProgram.objects.filter(
        start_time__gt=now,
        is_active=True
    ).order_by('start_time').first()
    
    # Today's timeline
    today = now.date()
    start_of_day = timezone.make_aware(datetime.combine(today, datetime.min.time()))
    end_of_day = timezone.make_aware(datetime.combine(today, datetime.max.time()))
    
    today_programs = FlashSaleProgram.objects.filter(
        start_time__gte=start_of_day,
        start_time__lte=end_of_day,
        is_active=True
    ).order_by('start_time')
    
    # Current sale items
    current_items = []
    if current_program:
        current_items = FlashSaleItem.objects.filter(
            program=current_program,
            is_active=True
        ).select_related('product').annotate(
            remaining=F('total_quantity') - F('sold_quantity')
        ).filter(remaining__gt=0)[:20]  # Limit to 20 items
    
    # Serialize data
    current_program_data = FlashSaleProgramSerializer(current_program).data if current_program else None
    next_program_data = FlashSaleProgramSerializer(next_program).data if next_program else None
    today_programs_data = FlashSaleProgramSerializer(today_programs, many=True).data
    current_items_data = FlashSaleItemSerializer(current_items, many=True).data
    
    return Response({
        'current_program': current_program_data,
        'next_program': next_program_data,
        'today_timeline': today_programs_data,
        'current_items': current_items_data,
        'server_time': now.isoformat(),
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def purchase_flash_sale_item(request):
    """Mua sản phẩm Flash Sale"""
    item_id = request.data.get('item_id')
    quantity = int(request.data.get('quantity', 1))
    
    if not item_id:
        return Response({'error': 'Thiếu item_id'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        item = FlashSaleItem.objects.select_related('program', 'product').get(id=item_id)
    except FlashSaleItem.DoesNotExist:
        return Response({'error': 'Sản phẩm không tồn tại'}, status=status.HTTP_404_NOT_FOUND)
    
    # Check if can purchase
    can_purchase, message = item.can_purchase(request.user, quantity)
    if not can_purchase:
        return Response({'error': message}, status=status.HTTP_400_BAD_REQUEST)
    
    # Create purchase record
    purchase = FlashSalePurchase.objects.create(
        item=item,
        user=request.user,
        quantity=quantity,
        price_paid=item.flash_price * quantity
    )
    
    # Update sold quantity
    item.sold_quantity = F('sold_quantity') + quantity
    item.save()
    item.refresh_from_db()
    
    # Serialize response
    purchase_data = FlashSalePurchaseSerializer(purchase).data
    item_data = FlashSaleItemSerializer(item).data
    
    return Response({
        'message': 'Mua hàng thành công',
        'purchase': purchase_data,
        'item': item_data
    }, status=status.HTTP_201_CREATED)


class FlashSaleTimeSlotViewSet(ModelViewSet):
    """ViewSet cho Flash Sale Time Slots"""
    queryset = FlashSaleTimeSlot.objects.all()
    serializer_class = FlashSaleTimeSlotSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        return FlashSaleTimeSlot.objects.filter(is_active=True).order_by('start_hour', 'start_minute')

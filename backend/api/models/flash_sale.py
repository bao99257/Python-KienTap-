from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from .product import Product


class FlashSaleProgram(models.Model):
    """Chương trình Flash Sale"""
    
    PROGRAM_STATUS = [
        ('upcoming', 'Sắp diễn ra'),
        ('active', 'Đang diễn ra'),
        ('ended', 'Đã kết thúc'),
        ('cancelled', 'Đã hủy'),
    ]
    
    name = models.CharField(max_length=200, verbose_name="Tên chương trình")
    description = models.TextField(blank=True, verbose_name="Mô tả")
    
    # Thời gian
    start_time = models.DateTimeField(verbose_name="Thời gian bắt đầu")
    end_time = models.DateTimeField(verbose_name="Thời gian kết thúc")
    
    # Trạng thái
    status = models.CharField(max_length=20, choices=PROGRAM_STATUS, default='upcoming')
    is_active = models.BooleanField(default=True, verbose_name="Kích hoạt")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='flash_sale_programs')
    
    class Meta:
        db_table = 'flash_sale_programs'
        verbose_name = "Chương trình Flash Sale"
        verbose_name_plural = "Chương trình Flash Sale"
        ordering = ['-start_time']
    
    def __str__(self):
        return f"{self.name} ({self.start_time.strftime('%H:%M %d/%m')})"
    
    @property
    def is_upcoming(self):
        """Kiểm tra chương trình sắp diễn ra"""
        return timezone.now() < self.start_time
    
    @property
    def is_running(self):
        """Kiểm tra chương trình đang diễn ra"""
        now = timezone.now()
        return self.start_time <= now <= self.end_time and self.is_active
    
    @property
    def is_ended(self):
        """Kiểm tra chương trình đã kết thúc"""
        return timezone.now() > self.end_time
    
    @property
    def time_remaining(self):
        """Thời gian còn lại (giây)"""
        if self.is_ended:
            return 0
        return max(0, int((self.end_time - timezone.now()).total_seconds()))
    
    def update_status(self):
        """Cập nhật trạng thái tự động"""
        if self.is_ended:
            self.status = 'ended'
        elif self.is_running:
            self.status = 'active'
        elif self.is_upcoming:
            self.status = 'upcoming'
        self.save()


class FlashSaleItem(models.Model):
    """Sản phẩm trong Flash Sale"""
    
    program = models.ForeignKey(FlashSaleProgram, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='flash_sale_items')
    
    # Giá và số lượng
    original_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Giá gốc")
    flash_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Giá Flash Sale")
    
    # Số lượng
    total_quantity = models.PositiveIntegerField(verbose_name="Tổng số lượng")
    sold_quantity = models.PositiveIntegerField(default=0, verbose_name="Đã bán")
    
    # Giới hạn
    max_per_user = models.PositiveIntegerField(default=1, verbose_name="Giới hạn mỗi người")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'flash_sale_items'
        verbose_name = "Sản phẩm Flash Sale"
        verbose_name_plural = "Sản phẩm Flash Sale"
        unique_together = ['program', 'product']
    
    def __str__(self):
        return f"{self.product.name} - {self.program.name}"
    
    @property
    def remaining_quantity(self):
        """Số lượng còn lại"""
        return max(0, self.total_quantity - self.sold_quantity)
    
    @property
    def sold_percentage(self):
        """Phần trăm đã bán"""
        if self.total_quantity == 0:
            return 0
        return min(100, (self.sold_quantity / self.total_quantity) * 100)
    
    @property
    def discount_percentage(self):
        """Phần trăm giảm giá"""
        if self.original_price == 0:
            return 0
        return int(((self.original_price - self.flash_price) / self.original_price) * 100)
    
    @property
    def is_available(self):
        """Kiểm tra còn hàng và chương trình đang chạy"""
        return (
            self.remaining_quantity > 0 and 
            self.program.is_running and 
            self.is_active
        )
    
    def can_purchase(self, user, quantity=1):
        """Kiểm tra user có thể mua không"""
        if not self.is_available:
            return False, "Sản phẩm không khả dụng"
        
        if quantity > self.remaining_quantity:
            return False, "Không đủ số lượng"
        
        # Kiểm tra giới hạn mỗi user
        user_purchased = FlashSalePurchase.objects.filter(
            item=self,
            user=user
        ).aggregate(total=models.Sum('quantity'))['total'] or 0
        
        if user_purchased + quantity > self.max_per_user:
            return False, f"Vượt quá giới hạn {self.max_per_user} sản phẩm/người"
        
        return True, "OK"


class FlashSalePurchase(models.Model):
    """Lịch sử mua Flash Sale"""
    
    item = models.ForeignKey(FlashSaleItem, on_delete=models.CASCADE, related_name='purchases')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='flash_sale_purchases')
    
    quantity = models.PositiveIntegerField(verbose_name="Số lượng")
    price_paid = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Giá đã trả")
    
    # Metadata
    purchased_at = models.DateTimeField(auto_now_add=True)
    order_id = models.CharField(max_length=100, blank=True, verbose_name="Mã đơn hàng")
    
    class Meta:
        db_table = 'flash_sale_purchases'
        verbose_name = "Lịch sử mua Flash Sale"
        verbose_name_plural = "Lịch sử mua Flash Sale"
        ordering = ['-purchased_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.item.product.name} x{self.quantity}"


class FlashSaleTimeSlot(models.Model):
    """Khung giờ Flash Sale trong ngày"""
    
    WEEKDAYS = [
        (0, 'Thứ 2'),
        (1, 'Thứ 3'),
        (2, 'Thứ 4'),
        (3, 'Thứ 5'),
        (4, 'Thứ 6'),
        (5, 'Thứ 7'),
        (6, 'Chủ nhật'),
    ]
    
    name = models.CharField(max_length=100, verbose_name="Tên khung giờ")
    start_hour = models.PositiveIntegerField(verbose_name="Giờ bắt đầu (0-23)")
    start_minute = models.PositiveIntegerField(default=0, verbose_name="Phút bắt đầu (0-59)")
    duration_minutes = models.PositiveIntegerField(default=120, verbose_name="Thời lượng (phút)")
    
    # Lặp lại
    weekdays = models.JSONField(default=list, verbose_name="Các ngày trong tuần")
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'flash_sale_time_slots'
        verbose_name = "Khung giờ Flash Sale"
        verbose_name_plural = "Khung giờ Flash Sale"
        ordering = ['start_hour', 'start_minute']
    
    def __str__(self):
        return f"{self.name} ({self.start_hour:02d}:{self.start_minute:02d})"
    
    @property
    def time_display(self):
        """Hiển thị thời gian"""
        return f"{self.start_hour:02d}:{self.start_minute:02d}"

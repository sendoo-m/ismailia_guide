from django.db import models
from django.utils import timezone
from directory.models import Business

class SubscriptionPlan(models.Model):
    PLAN_CHOICES = (
        ('free', 'مجاني'),
        ('basic', 'أساسي'),
        ('premium', 'مميز'),
        ('vip', 'VIP'),
    )
    
    name = models.CharField(
        max_length=20,
        choices=PLAN_CHOICES,
        unique=True,
        verbose_name='اسم الخطة'
    )
    display_name = models.CharField(max_length=50, verbose_name='الاسم المعروض')
    price_yearly = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='السعر السنوي'
    )
    max_products = models.PositiveIntegerField(
        verbose_name='الحد الأقصى للمنتجات',
        help_text='اكتب 0 لغير محدود'
    )
    can_upload_images = models.BooleanField(
        default=False,
        verbose_name='رفع صور المنتجات'
    )
    show_prices = models.BooleanField(
        default=False,
        verbose_name='عرض الأسعار'
    )
    has_delivery_options = models.BooleanField(
        default=False,
        verbose_name='خيارات التوصيل'
    )
    featured_in_search = models.BooleanField(
        default=False,
        verbose_name='أولوية في نتائج البحث'
    )
    description = models.TextField(blank=True, verbose_name='الوصف')
    is_active = models.BooleanField(default=True, verbose_name='نشط')
    
    class Meta:
        verbose_name = 'خطة اشتراك'
        verbose_name_plural = 'خطط الاشتراك'
        ordering = ['price_yearly']
    
    def __str__(self):
        return f"{self.display_name} - {self.price_yearly} جنيه/سنة"


class Subscription(models.Model):
    STATUS_CHOICES = (
        ('active', 'نشط'),
        ('expired', 'منتهي'),
        ('cancelled', 'ملغي'),
    )
    
    business = models.OneToOneField(
        Business,
        on_delete=models.CASCADE,
        related_name='subscription',
        verbose_name='المحل'
    )
    plan = models.ForeignKey(
        SubscriptionPlan,
        on_delete=models.PROTECT,
        related_name='subscriptions',
        verbose_name='الخطة'
    )
    start_date = models.DateTimeField(verbose_name='تاريخ البداية')
    end_date = models.DateTimeField(verbose_name='تاريخ الانتهاء')
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='active',
        verbose_name='الحالة'
    )
    auto_renew = models.BooleanField(default=False, verbose_name='تجديد تلقائي')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاريخ التحديث')
    
    class Meta:
        verbose_name = 'اشتراك'
        verbose_name_plural = 'الاشتراكات'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.business.name} - {self.plan.display_name}"
    
    @property
    def is_active(self):
        """التحقق من نشاط الاشتراك"""
        return self.status == 'active' and self.end_date > timezone.now()
    
    @property
    def days_remaining(self):
        """عدد الأيام المتبقية"""
        if self.is_active:
            delta = self.end_date - timezone.now()
            return delta.days
        return 0

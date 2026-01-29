from django.db import models
from directory.models import Business
from subscriptions.models import Subscription

class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = (
        ('paymob', 'Paymob'),
        ('fawry', 'فوري'),
        ('bank_transfer', 'تحويل بنكي'),
        ('cash', 'كاش'),
    )
    
    STATUS_CHOICES = (
        ('pending', 'قيد الانتظار'),
        ('completed', 'مكتمل'),
        ('failed', 'فشل'),
        ('refunded', 'مُسترد'),
    )
    
    business = models.ForeignKey(
        Business,
        on_delete=models.CASCADE,
        related_name='payments',
        verbose_name='المحل'
    )
    subscription = models.ForeignKey(
        Subscription,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='payments',
        verbose_name='الاشتراك'
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='المبلغ'
    )
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        verbose_name='طريقة الدفع'
    )
    transaction_id = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='رقم العملية'
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='الحالة'
    )
    notes = models.TextField(blank=True, verbose_name='ملاحظات')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاريخ التحديث')
    
    class Meta:
        verbose_name = 'دفعة'
        verbose_name_plural = 'المدفوعات'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.business.name} - {self.amount} جنيه ({self.get_status_display()})"

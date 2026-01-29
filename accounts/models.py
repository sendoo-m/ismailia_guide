from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('admin', 'مدير النظام'),
        ('vendor', 'صاحب محل'),
        ('customer', 'عميل'),
    )
    
    user_type = models.CharField(
        max_length=10,
        choices=USER_TYPE_CHOICES,
        default='customer',
        verbose_name='نوع المستخدم'
    )
    phone = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        verbose_name='رقم الهاتف'
    )
    is_verified = models.BooleanField(
        default=False,
        verbose_name='تم التحقق'
    )
    
    class Meta:
        verbose_name = 'مستخدم'
        verbose_name_plural = 'المستخدمون'
    
    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"

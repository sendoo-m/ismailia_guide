from django.db import models
from directory.models import Business

class Product(models.Model):
    business = models.ForeignKey(
        Business,
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name='المحل'
    )
    name = models.CharField(max_length=200, verbose_name='اسم المنتج/الخدمة')
    slug = models.SlugField(max_length=200, blank=True)
    description = models.TextField(verbose_name='الوصف')
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='السعر',
        help_text='بالجنيه المصري'
    )
    is_available = models.BooleanField(default=True, verbose_name='متوفر')
    has_delivery = models.BooleanField(default=False, verbose_name='يوجد توصيل')
    delivery_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='تكلفة التوصيل'
    )
    order = models.IntegerField(default=0, verbose_name='الترتيب')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإضافة')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاريخ التحديث')
    
    class Meta:
        verbose_name = 'منتج'
        verbose_name_plural = 'المنتجات'
        ordering = ['order', '-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.business.name}"


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name='المنتج'
    )
    image = models.ImageField(upload_to='products/', verbose_name='الصورة')
    is_primary = models.BooleanField(default=False, verbose_name='صورة رئيسية')
    order = models.IntegerField(default=0, verbose_name='الترتيب')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإضافة')
    
    class Meta:
        verbose_name = 'صورة منتج'
        verbose_name_plural = 'صور المنتجات'
        ordering = ['order', '-created_at']
    
    def __str__(self):
        return f"صورة {self.product.name}"

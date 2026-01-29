from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.core.validators import RegexValidator
from django.urls import reverse
from django.db.models import Count, Q

from accounts.models import User


# ========================================
# نموذج المحافظات
# ========================================
class Governorate(models.Model):
    """نموذج المحافظات المصرية"""
    
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='اسم المحافظة',
        help_text='مثال: الإسماعيلية، الشرقية، بورسعيد',
        db_index=True
    )
    slug = models.SlugField(
        max_length=100,
        unique=True,
        blank=True,
        allow_unicode=True,
        verbose_name='الرابط'
    )
    description = models.TextField(
        blank=True,
        verbose_name='الوصف',
        help_text='معلومات عن المحافظة (اختياري)'
    )
    icon = models.CharField(
        max_length=50,
        blank=True,
        default='fas fa-city',
        verbose_name='أيقونة Font Awesome',
        help_text='مثال: fas fa-city'
    )
    image = models.ImageField(
        upload_to='governorates/%Y/%m/',
        blank=True,
        null=True,
        verbose_name='صورة المحافظة',
        help_text='صورة تمثيلية للمحافظة (اختياري)'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='نشط',
        help_text='إلغاء التفعيل يخفي المحافظة من الموقع'
    )
    order = models.IntegerField(
        default=0,
        verbose_name='الترتيب',
        help_text='رقم أصغر = يظهر أولاً'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='تاريخ الإنشاء'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='تاريخ التحديث'
    )
    
    class Meta:
        verbose_name = 'محافظة'
        verbose_name_plural = 'المحافظات'
        ordering = ['order', 'name']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['is_active', 'order']),
        ]
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        """رابط صفحة المحافظة"""
        return reverse('governorate_detail', kwargs={'slug': self.slug})
    
    def get_business_count(self):
        """عدد المحلات النشطة والموثقة في المحافظة"""
        return self.districts.filter(
            is_active=True
        ).aggregate(
            count=Count(
                'businesses',
                filter=Q(businesses__is_active=True, businesses__is_verified=True),
                distinct=True
            )
        )['count'] or 0
    
    def get_districts_count(self):
        """عدد الأحياء النشطة في المحافظة"""
        return self.districts.filter(is_active=True).count()


# ========================================
# نموذج الفئات
# ========================================
class Category(models.Model):
    """نموذج الفئات (مطاعم، محلات، خدمات، إلخ)"""
    
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='اسم الفئة',
        help_text='مثال: مطاعم ومقاهي، صيدليات، محلات ملابس',
        db_index=True
    )
    slug = models.SlugField(
        max_length=100,
        unique=True,
        blank=True,
        allow_unicode=True,
        verbose_name='الرابط'
    )
    icon = models.CharField(
        max_length=50,
        blank=True,
        default='fas fa-store',
        verbose_name='أيقونة Font Awesome',
        help_text='مثال: fas fa-utensils'
    )
    description = models.TextField(
        blank=True,
        verbose_name='الوصف',
        help_text='وصف تفصيلي للفئة (اختياري)'
    )
    image = models.ImageField(
        upload_to='categories/%Y/%m/',
        blank=True,
        null=True,
        verbose_name='صورة الفئة',
        help_text='صورة تمثيلية للفئة (اختياري)'
    )
    order = models.IntegerField(
        default=0,
        verbose_name='الترتيب',
        help_text='رقم أصغر = يظهر أولاً'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='نشط',
        help_text='إلغاء التفعيل يخفي الفئة من الموقع'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='تاريخ الإنشاء'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='تاريخ التحديث'
    )
    
    class Meta:
        verbose_name = 'فئة'
        verbose_name_plural = 'الفئات'
        ordering = ['order', 'name']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['is_active', 'order']),
        ]
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        """رابط صفحة الفئة"""
        return reverse('category_detail', kwargs={'slug': self.slug})
    
    def get_business_count(self):
        """عدد المحلات النشطة في الفئة"""
        return self.businesses.filter(is_active=True, is_verified=True).count()


# ========================================
# نموذج الأحياء
# ========================================
class District(models.Model):
    """نموذج الأحياء"""
    
    governorate = models.ForeignKey(
        'Governorate',
        on_delete=models.CASCADE,
        related_name='districts',
        related_query_name='district',
        verbose_name='المحافظة'
    )
    name = models.CharField(
        max_length=100,
        verbose_name='اسم الحي',
        db_index=True
    )
    slug = models.SlugField(
        max_length=100,
        unique=True,
        blank=True,
        allow_unicode=True,
        verbose_name='الرابط'
    )
    description = models.TextField(
        blank=True,
        verbose_name='الوصف',
        help_text='وصف تفصيلي للحي (اختياري)'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='نشط'
    )
    order = models.IntegerField(
        default=0,
        verbose_name='الترتيب'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='تاريخ الإنشاء'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='تاريخ التحديث'
    )
    
    class Meta:
        verbose_name = 'حي'
        verbose_name_plural = 'الأحياء'
        ordering = ['governorate__order', 'governorate__name', 'order', 'name']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['governorate', 'is_active']),
            models.Index(fields=['is_active', 'order']),
        ]
        unique_together = [['governorate', 'name']]  # منع تكرار اسم الحي في نفس المحافظة
    
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(f"{self.governorate.name}-{self.name}", allow_unicode=True)
            slug = base_slug
            counter = 1
            while District.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.name} - {self.governorate.name}"
    
    def get_absolute_url(self):
        """رابط صفحة الحي"""
        return reverse('district_detail', kwargs={'slug': self.slug})
    
    def get_business_count(self):
        """عدد المحلات النشطة في الحي"""
        return self.businesses.filter(is_active=True, is_verified=True).count()


# ========================================
# نموذج المحلات التجارية
# ========================================
class Business(models.Model):
    """نموذج المحلات التجارية"""
    
    # Phone validator
    phone_regex = RegexValidator(
        regex=r'^01[0-2,5]{1}[0-9]{8}$',
        message="أدخل رقم هاتف مصري صحيح (مثال: 01234567890)"
    )
    
    # Owner
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='businesses',
        related_query_name='business',
        verbose_name='المالك'
    )
    
    # Basic Info
    name = models.CharField(
        max_length=200,
        verbose_name='اسم المحل',
        db_index=True
    )
    slug = models.SlugField(
        max_length=250,
        unique=True,
        blank=True,
        allow_unicode=True,
        verbose_name='الرابط'
    )
    logo = models.ImageField(
        upload_to='businesses/logos/%Y/%m/',
        blank=True,
        null=True,
        verbose_name='اللوجو',
        help_text='يُفضل صورة مربعة 500x500 بكسل'
    )
    
    # Classification
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='businesses',
        related_query_name='business',
        verbose_name='الفئة'
    )
    district = models.ForeignKey(
        District,
        on_delete=models.PROTECT,
        related_name='businesses',
        related_query_name='business',
        verbose_name='الحي'
    )
    
    # Contact Information
    phone = models.CharField(
        max_length=15,
        validators=[phone_regex],
        verbose_name='رقم الهاتف',
        help_text='مثال: 01234567890'
    )
    whatsapp = models.CharField(
        max_length=15,
        blank=True,
        validators=[phone_regex],
        verbose_name='واتساب',
        help_text='رقم واتساب (اختياري)'
    )
    email = models.EmailField(
        blank=True,
        verbose_name='البريد الإلكتروني'
    )
    website = models.URLField(
        blank=True,
        verbose_name='الموقع الإلكتروني',
        help_text='رابط الموقع الإلكتروني للمحل (اختياري)'
    )
    
    # Social Media
    facebook = models.URLField(
        blank=True,
        verbose_name='فيسبوك',
        help_text='رابط صفحة الفيسبوك (اختياري)'
    )
    instagram = models.URLField(
        blank=True,
        verbose_name='إنستجرام',
        help_text='رابط حساب الإنستجرام (اختياري)'
    )
    twitter = models.URLField(
        blank=True,
        verbose_name='تويتر',
        help_text='رابط حساب تويتر (اختياري)'
    )
    
    # Location
    address = models.TextField(
        verbose_name='العنوان',
        help_text='العنوان التفصيلي للمحل'
    )
    location_url = models.URLField(
        blank=True,
        verbose_name='رابط الموقع (Google Maps)',
        help_text='رابط موقع المحل على خرائط جوجل (اختياري)'
    )
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        verbose_name='خط العرض',
        help_text='يتم تحديده تلقائياً من الخريطة'
    )
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        verbose_name='خط الطول',
        help_text='يتم تحديده تلقائياً من الخريطة'
    )
    
    # Description
    description = models.TextField(
        verbose_name='الوصف',
        help_text='وصف تفصيلي عن المحل والخدمات المقدمة'
    )
    working_hours = models.TextField(
        blank=True,
        verbose_name='ساعات العمل',
        help_text='مثال: السبت-الخميس: 9 صباحاً - 10 مساءً | الجمعة: 2 مساءً - 10 مساءً'
    )
    
    # Statistics
    view_count = models.PositiveIntegerField(
        default=0,
        verbose_name='عدد المشاهدات',
        editable=False
    )
    
    # Status
    is_active = models.BooleanField(
        default=False,
        verbose_name='نشط',
        help_text='تفعيل/إيقاف ظهور المحل في الموقع'
    )
    is_verified = models.BooleanField(
        default=False,
        verbose_name='موثّق',
        help_text='تم التحقق من صحة المحل'
    )
    is_featured = models.BooleanField(
        default=False,
        verbose_name='مميز',
        help_text='عرض المحل في قسم المحلات المميزة'
    )
    
    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='تاريخ الإضافة'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='تاريخ التحديث'
    )
    
    logo = models.ImageField(
        upload_to='businesses/logos/%Y/%m/',
        blank=True,
        null=True,
        verbose_name='اللوجو',
        help_text='يُفضل صورة مربعة 500x500 بكسل'
    )
    
    # ✨ إضافة صورة الغلاف (جديد)
    cover_image = models.ImageField(
        upload_to='businesses/covers/%Y/%m/',
        blank=True,
        null=True,
        verbose_name='صورة الغلاف',
        help_text='صورة عريضة للعرض في البطاقة والبانر (يُفضل 1200x400 بكسل)'
    )    

    class Meta:
        verbose_name = 'محل'
        verbose_name_plural = 'المحلات'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['is_active', 'is_verified']),
            models.Index(fields=['category', 'is_active']),
            models.Index(fields=['district', 'is_active']),
            models.Index(fields=['-view_count']),
            models.Index(fields=['is_featured']),
            models.Index(fields=['owner', 'is_active']),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(latitude__gte=-90, latitude__lte=90) | models.Q(latitude__isnull=True),
                name='valid_latitude',
                violation_error_message='خط العرض يجب أن يكون بين -90 و 90'
            ),
            models.CheckConstraint(
                condition=models.Q(longitude__gte=-180, longitude__lte=180) | models.Q(longitude__isnull=True),
                name='valid_longitude',
                violation_error_message='خط الطول يجب أن يكون بين -180 و 180'
            ),
        ]
    
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name, allow_unicode=True)
            slug = base_slug
            counter = 1
            while Business.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.name} - {self.district.name}"
    
    def get_absolute_url(self):
        """رابط صفحة المحل"""
        return reverse('business_detail', kwargs={'slug': self.slug})
    
    @property
    def governorate(self):
        """المحافظة التابع لها المحل"""
        return self.district.governorate
    
    @property
    def average_rating(self):
        """حساب متوسط التقييمات"""
        from django.db.models import Avg
        try:
            from reviews.models import Review
            reviews = Review.objects.filter(business=self, is_approved=True)
            if reviews.exists():
                avg = reviews.aggregate(Avg('rating'))['rating__avg']
                return round(avg, 1) if avg else 0
        except ImportError:
            pass
        return 0
    
    @property
    def total_reviews(self):
        """عدد التقييمات المُعتمدة"""
        try:
            from reviews.models import Review
            return Review.objects.filter(business=self, is_approved=True).count()
        except ImportError:
            return 0
    
    @property
    def has_location(self):
        """هل للمحل موقع جغرافي محدد؟"""
        return self.latitude is not None and self.longitude is not None
    
    @property
    def subscription(self):
        """الحصول على اشتراك المحل الحالي"""
        try:
            from subscriptions.models import Subscription
            return Subscription.objects.filter(business=self, status='active').first()
        except ImportError:
            return None
    
    @property
    def can_add_products(self):
        """هل يمكن إضافة منتجات؟"""
        sub = self.subscription
        if not sub:
            return False
        
        try:
            from products.models import Product
            current_products = Product.objects.filter(business=self).count()
            max_products = sub.plan.max_products
            
            if max_products == 0:  # unlimited
                return True
            
            return current_products < max_products
        except ImportError:
            return False
    
    def increment_view_count(self):
        """زيادة عداد المشاهدات"""
        self.view_count = models.F('view_count') + 1
        self.save(update_fields=['view_count'])
        self.refresh_from_db()


# ========================================
# نموذج صور المحلات
# ========================================
class BusinessImage(models.Model):
    """نموذج صور المحلات التجارية"""
    
    business = models.ForeignKey(
        Business,
        on_delete=models.CASCADE,
        related_name='images',
        related_query_name='image',
        verbose_name='المحل'
    )
    image = models.ImageField(
        upload_to='businesses/images/%Y/%m/',
        verbose_name='الصورة'
    )
    caption = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='وصف الصورة'
    )
    order = models.IntegerField(
        default=0,
        verbose_name='الترتيب'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='نشط'
    )
    uploaded_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='تاريخ الرفع'
    )
    
    class Meta:
        verbose_name = 'صورة محل'
        verbose_name_plural = 'صور المحلات'
        ordering = ['order', '-uploaded_at']
        indexes = [
            models.Index(fields=['business', 'is_active']),
        ]
    
    def __str__(self):
        return f"صورة - {self.business.name}"

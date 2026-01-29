from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.db.models import Count, Q
from .models import Governorate, Category, District, Business, BusinessImage
from products.models import Product


# ========================================
# تخصيص Admin Site
# ========================================
admin.site.site_header = "دليل الإسماعيلية - لوحة التحكم"
admin.site.site_title = "دليل الإسماعيلية"
admin.site.index_title = "مرحباً بك في لوحة التحكم"


# ========================================
# Governorate Admin
# ========================================
@admin.register(Governorate)
class GovernorateAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon_preview', 'order', 'is_active', 'get_districts_count', 'get_businesses_count', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['order', 'name']
    list_editable = ['order', 'is_active']
    
    fieldsets = (
        ('المعلومات الأساسية', {
            'fields': ('name', 'slug', 'icon', 'description', 'image')
        }),
        ('الإعدادات', {
            'fields': ('order', 'is_active')
        }),
        ('معلومات إضافية', {
            'classes': ('collapse',),
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def icon_preview(self, obj):
        if obj.icon:
            return mark_safe(f'<i class="{obj.icon}" style="font-size: 24px; color: #667eea;"></i>')
        return '-'
    icon_preview.short_description = 'الأيقونة'
    
    def get_districts_count(self, obj):
        """عدد الأحياء في المحافظة"""
        count = obj.districts.filter(is_active=True).count()
        return mark_safe(f'<span style="background: #17a2b8; color: white; padding: 5px 10px; border-radius: 5px;">{count}</span>')
    get_districts_count.short_description = 'عدد الأحياء'
    
    def get_businesses_count(self, obj):
        """عدد المحلات في المحافظة - ✅ استخدم district__business"""
        count = Business.objects.filter(
            district__governorate=obj,
            is_active=True,
            is_verified=True
        ).count()
        return mark_safe(f'<span style="background: #28a745; color: white; padding: 5px 10px; border-radius: 5px;">{count}</span>')
    get_businesses_count.short_description = 'عدد المحلات'
    
    def get_queryset(self, request):
        """تحسين الأداء"""
        qs = super().get_queryset(request)
        return qs.prefetch_related('districts')


# ========================================
# Category Admin
# ========================================
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon_preview', 'order', 'is_active', 'business_count']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at', 'updated_at']
    list_editable = ['order', 'is_active']
    
    fieldsets = (
        ('المعلومات الأساسية', {
            'fields': ('name', 'slug', 'icon', 'description', 'image')
        }),
        ('الإعدادات', {
            'fields': ('order', 'is_active')
        }),
        ('معلومات إضافية', {
            'classes': ('collapse',),
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def icon_preview(self, obj):
        if obj.icon:
            return mark_safe(f'<i class="{obj.icon}" style="font-size: 24px; color: #667eea;"></i>')
        return '-'
    icon_preview.short_description = 'الأيقونة'
    
    def business_count(self, obj):
        """عدد المحلات في الفئة"""
        count = obj.get_business_count()
        return mark_safe(f'<span style="background: #28a745; color: white; padding: 5px 10px; border-radius: 5px;">{count}</span>')
    business_count.short_description = 'عدد المحلات'


# ========================================
# District Admin
# ========================================
@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ['name', 'governorate', 'order', 'is_active', 'business_count', 'created_at']
    list_filter = ['governorate', 'is_active', 'created_at']
    search_fields = ['name', 'governorate__name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['governorate__order', 'governorate__name', 'order', 'name']
    list_editable = ['order', 'is_active']
    
    fieldsets = (
        ('المعلومات الأساسية', {
            'fields': ('governorate', 'name', 'slug', 'description')
        }),
        ('الإعدادات', {
            'fields': ('order', 'is_active')
        }),
        ('معلومات إضافية', {
            'classes': ('collapse',),
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def business_count(self, obj):
        """عدد المحلات في الحي"""
        count = obj.get_business_count()
        return mark_safe(f'<span style="background: #17a2b8; color: white; padding: 5px 10px; border-radius: 5px;">{count}</span>')
    business_count.short_description = 'عدد المحلات'
    
    def get_queryset(self, request):
        """تحسين الأداء"""
        qs = super().get_queryset(request)
        return qs.select_related('governorate')


# ========================================
# Business Image Inline
# ========================================
class BusinessImageInline(admin.TabularInline):
    model = BusinessImage
    extra = 1
    fields = ['image', 'caption', 'order', 'is_active']
    readonly_fields = ['uploaded_at']


# ========================================
# Product Inline (للـ Business)
# ========================================
class ProductInline(admin.TabularInline):
    model = Product
    extra = 0
    fields = ['name', 'price', 'is_available', 'order']
    readonly_fields = []


# ========================================
# Business Admin
# ========================================
@admin.register(Business)
class BusinessAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'owner', 'category', 'district', 'governorate_display',
        'status_badge', 'view_count', 'created_at'
    ]
    list_filter = [
        'is_active', 'is_verified', 'is_featured',
        'category', 'district__governorate', 'district',
        'created_at'
    ]
    search_fields = [
        'name', 'description', 'address',
        'owner__username', 'phone', 'email'
    ]
    readonly_fields = ['view_count', 'created_at', 'updated_at']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [BusinessImageInline, ProductInline]
    date_hierarchy = 'created_at'
    list_per_page = 25
    
    fieldsets = (
        ('معلومات أساسية', {
            'fields': ('name', 'slug', 'owner', 'category', 'district', 'cover_image', 'logo')
        }),
        ('معلومات الاتصال', {
            'fields': ('phone', 'whatsapp', 'email', 'website')
        }),
        ('وسائل التواصل الاجتماعي', {
            'classes': ('collapse',),
            'fields': ('facebook', 'instagram', 'twitter')
        }),
        ('الموقع', {
            'fields': ('address', 'location_url', 'latitude', 'longitude')
        }),
        ('التفاصيل', {
            'fields': ('description', 'working_hours')
        }),
        ('الحالة', {
            'fields': ('is_active', 'is_verified', 'is_featured')
        }),
        ('الإحصائيات', {
            'classes': ('collapse',),
            'fields': ('view_count', 'created_at', 'updated_at')
        }),
    )
    
    def governorate_display(self, obj):
        """عرض المحافظة"""
        return obj.district.governorate.name
    governorate_display.short_description = 'المحافظة'
    governorate_display.admin_order_field = 'district__governorate__name'
    
    def status_badge(self, obj):
        """عرض حالة المحل بشكل مرئي"""
        if obj.is_verified and obj.is_active:
            return mark_safe('<span style="background: #28a745; color: white; padding: 5px 10px; border-radius: 5px; white-space: nowrap;">✅ نشط ومُفعّل</span>')
        elif obj.is_active and not obj.is_verified:
            return mark_safe('<span style="background: #ffc107; color: #333; padding: 5px 10px; border-radius: 5px; white-space: nowrap;">⏳ بانتظار التفعيل</span>')
        elif not obj.is_active and obj.is_verified:
            return mark_safe('<span style="background: #6c757d; color: white; padding: 5px 10px; border-radius: 5px; white-space: nowrap;">⏸️ موقوف مؤقتاً</span>')
        else:
            return mark_safe('<span style="background: #dc3545; color: white; padding: 5px 10px; border-radius: 5px; white-space: nowrap;">❌ غير نشط</span>')
    status_badge.short_description = 'الحالة'
    
    # إجراءات مجمعة
    actions = ['activate_businesses', 'deactivate_businesses', 'verify_businesses']
    
    def activate_businesses(self, request, queryset):
        """تفعيل المحلات المحددة"""
        count = queryset.update(is_active=True)
        self.message_user(request, f'✅ تم تفعيل {count} محل بنجاح.')
    activate_businesses.short_description = '✅ تفعيل المحلات المحددة'
    
    def deactivate_businesses(self, request, queryset):
        """إيقاف المحلات المحددة"""
        count = queryset.update(is_active=False)
        self.message_user(request, f'⏸️ تم إيقاف {count} محل بنجاح.')
    deactivate_businesses.short_description = '⏸️ إيقاف المحلات المحددة'
    
    def verify_businesses(self, request, queryset):
        """التحقق من المحلات وتفعيلها"""
        count = queryset.update(is_verified=True, is_active=True)
        self.message_user(request, f'✔️ تم التحقق من {count} محل وتفعيله بنجاح.')
    verify_businesses.short_description = '✔️ التحقق من المحلات وتفعيلها'
    
    def get_queryset(self, request):
        """تحسين الأداء بـ select_related"""
        qs = super().get_queryset(request)
        return qs.select_related(
            'owner', 'category', 'district', 'district__governorate'
        )


# ========================================
# Business Image Admin
# ========================================
@admin.register(BusinessImage)
class BusinessImageAdmin(admin.ModelAdmin):
    list_display = ['business', 'caption', 'order', 'is_active', 'uploaded_at']
    list_filter = ['is_active', 'uploaded_at']
    search_fields = ['business__name', 'caption']
    list_editable = ['order', 'is_active']
    readonly_fields = ['uploaded_at']
    
    fieldsets = (
        ('المعلومات الأساسية', {
            'fields': ('business', 'image', 'caption')
        }),
        ('الإعدادات', {
            'fields': ('order', 'is_active')
        }),
        ('معلومات إضافية', {
            'classes': ('collapse',),
            'fields': ('uploaded_at',)
        }),
    )

from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from .models import SubscriptionPlan, Subscription


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = [
        'display_name', 
        'price_badge', 
        'max_products_display', 
        'features_summary', 
        'is_active'
    ]
    list_filter = ['is_active', 'featured_in_search']
    search_fields = ['display_name', 'description']
    readonly_fields = ['created_at', 'updated_at'] if hasattr(SubscriptionPlan, 'created_at') else []
    
    fieldsets = (
        ('معلومات أساسية', {
            'fields': ('name', 'display_name', 'price_yearly', 'is_active')
        }),
        ('المميزات', {
            'fields': ('max_products', 'can_upload_images', 'show_prices', 
                      'has_delivery_options', 'featured_in_search')
        }),
        ('الوصف', {
            'fields': ('description',)
        }),
    )
    
    def price_badge(self, obj):
        """عرض السعر مع badge ملون"""
        if obj.price_yearly == 0:
            # ✅ حل: اكتب الـ HTML في سطر واحد
            return mark_safe('<span style="background: #28a745; color: white; padding: 5px 10px; border-radius: 5px; font-weight: bold;">مجاني</span>')
        # ✅ حل: استخدم format مع string في سطر واحد
        return mark_safe(f'<span style="background: #667eea; color: white; padding: 5px 10px; border-radius: 5px; font-weight: bold;">{obj.price_yearly} جنيه/سنة</span>')
    price_badge.short_description = 'السعر'
    
    def max_products_display(self, obj):
        """عرض الحد الأقصى للمنتجات"""
        if obj.max_products == 0:
            return mark_safe('<span style="color: #28a745; font-weight: bold;">غير محدود ∞</span>')
        return mark_safe(f'<span style="color: #667eea; font-weight: bold;">{obj.max_products} منتج</span>')
    max_products_display.short_description = 'المنتجات'
    
    def features_summary(self, obj):
        """ملخص المميزات"""
        features = []
        if obj.can_upload_images:
            features.append('📷 صور')
        if obj.show_prices:
            features.append('💰 أسعار')
        if obj.has_delivery_options:
            features.append('🚚 توصيل')
        if obj.featured_in_search:
            features.append('⭐ مميز')
        
        if features:
            return mark_safe(' | '.join(features))
        return '-'
    features_summary.short_description = 'المميزات'


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = [
        'business', 
        'plan', 
        'status_badge', 
        'start_date', 
        'end_date', 
        'days_remaining_display', 
        'auto_renew'
    ]
    list_filter = ['status', 'auto_renew', 'plan']
    search_fields = ['business__name', 'business__owner__username']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'start_date'
    
    fieldsets = (
        ('معلومات الاشتراك', {
            'fields': ('business', 'plan', 'status')
        }),
        ('المدة', {
            'fields': ('start_date', 'end_date', 'auto_renew')
        }),
        ('معلومات إضافية', {
            'classes': ('collapse',),
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def status_badge(self, obj):
        """عرض حالة الاشتراك مع badge ملون"""
        colors = {
            'active': '#28a745',
            'expired': '#dc3545',
            'cancelled': '#6c757d',
        }
        color = colors.get(obj.status, '#6c757d')
        return mark_safe(f'<span style="background: {color}; color: white; padding: 5px 10px; border-radius: 5px; font-weight: bold;">{obj.get_status_display()}</span>')
    status_badge.short_description = 'الحالة'
    
    def days_remaining_display(self, obj):
        """عرض الأيام المتبقية"""
        days = obj.days_remaining
        if days > 0:
            return mark_safe(f'<span style="color: #28a745; font-weight: bold;">{days} يوم</span>')
        return mark_safe('<span style="color: #dc3545; font-weight: bold;">منتهي</span>')
    days_remaining_display.short_description = 'المتبقي'

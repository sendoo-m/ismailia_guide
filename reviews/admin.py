from django.contrib import admin
from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'reviewer_name',  # ← Method موجود دلوقتي
        'business',
        'rating',
        'is_approved',  # ← Field موجود دلوقتي
        'created_at'
    ]
    list_filter = [
        'is_approved',  # ← Field موجود دلوقتي
        'rating',
        'created_at'
    ]
    list_editable = ['is_approved']  # ← Field موجود دلوقتي
    search_fields = [
        'user__username',
        'user__first_name',
        'user__last_name',
        'business__name',
        'comment'
    ]
    readonly_fields = ['created_at', 'updated_at']
    list_per_page = 25
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('معلومات التقييم', {
            'fields': ('business', 'user', 'rating', 'comment')
        }),
        ('الحالة', {
            'fields': ('is_approved',)
        }),
        ('التواريخ', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def reviewer_name(self, obj):
        """عرض اسم المراجع"""
        return obj.user.get_full_name() or obj.user.username
    reviewer_name.short_description = 'المراجع'
    reviewer_name.admin_order_field = 'user__username'
    
    actions = ['approve_reviews', 'reject_reviews']
    
    def approve_reviews(self, request, queryset):
        """الموافقة على التقييمات المحددة"""
        updated = queryset.update(is_approved=True)
        self.message_user(request, f'تم الموافقة على {updated} تقييم.')
    approve_reviews.short_description = 'الموافقة على التقييمات المحددة'
    
    def reject_reviews(self, request, queryset):
        """رفض التقييمات المحددة"""
        updated = queryset.update(is_approved=False)
        self.message_user(request, f'تم رفض {updated} تقييم.')
    reject_reviews.short_description = 'رفض التقييمات المحددة'

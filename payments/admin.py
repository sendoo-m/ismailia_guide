from django.contrib import admin
from django.utils.html import format_html
from .models import Payment

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = [
        'business', 'amount', 'payment_method', 
        'status_display', 'transaction_id', 'created_at'
    ]
    list_filter = ['status', 'payment_method', 'created_at']
    search_fields = ['business__name', 'transaction_id', 'notes']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('معلومات الدفعة', {
            'fields': ('business', 'subscription', 'amount')
        }),
        ('تفاصيل الدفع', {
            'fields': ('payment_method', 'transaction_id', 'status')
        }),
        ('ملاحظات', {
            'fields': ('notes',)
        }),
        ('التواريخ', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def status_display(self, obj):
        colors = {
            'pending': '#FFA500',
            'completed': '#28a745',
            'failed': '#dc3545',
            'refunded': '#6c757d'
        }
        color = colors.get(obj.status, '#000')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.get_status_display()
        )
    status_display.short_description = 'الحالة'

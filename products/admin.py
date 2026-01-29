from django.contrib import admin
from django.utils.html import format_html

from import_export import resources
from import_export.admin import ImportExportModelAdmin

from .models import Product, ProductImage


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ['image', 'is_primary', 'order', 'image_preview']
    readonly_fields = ['image_preview']

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="100" height="100" style="object-fit: cover;" />',
                obj.image.url
            )
        return '—'
    image_preview.short_description = 'معاينة'


class ProductResource(resources.ModelResource):
    class Meta:
        model = Product
        fields = (
            'id',
            'business__name',
            'name',
            'description',
            'price',
            'is_available',
            'has_delivery',
        )
        export_order = (
            'id',
            'business__name',
            'name',
            'description',
            'price',
            'is_available',
            'has_delivery',
        )


@admin.register(Product)
class ProductAdmin(ImportExportModelAdmin):
    resource_class = ProductResource

    list_display = [
        'name',
        'business',
        'price',
        'is_available',
        'has_delivery',
        'order',
        'created_at',
    ]
    list_filter = ['is_available', 'has_delivery', 'business__category', 'created_at']
    search_fields = ['name', 'description', 'business__name']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['is_available', 'order']
    inlines = [ProductImageInline]

    fieldsets = (
        ('معلومات المنتج', {
            'fields': ('business', 'name', 'slug', 'description'),
        }),
        ('السعر والتوصيل', {
            'fields': ('price', 'has_delivery', 'delivery_cost'),
        }),
        ('الحالة', {
            'fields': ('is_available', 'order'),
        }),
    )


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['product', 'image_preview', 'is_primary', 'order', 'created_at']
    list_filter = ['is_primary', 'created_at']
    search_fields = ['product__name']
    list_editable = ['is_primary', 'order']

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="80" height="80" style="object-fit: cover;" />',
                obj.image.url
            )
        return '—'
    image_preview.short_description = 'الصورة'

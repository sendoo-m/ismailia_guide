from django import template
from django.conf import settings

register = template.Library()

@register.simple_tag
def get_default_seo():
    """إرجاع قيم SEO الافتراضية"""
    return {
        'site_name': getattr(settings, 'SITE_NAME', 'دليل الإسماعيلية'),
        'title': 'دليل الإسماعيلية - دليل شامل للمحلات والخدمات',
        'description': 'دليل شامل للمحلات التجارية والخدمات في الإسماعيلية والمحافظات المجاورة',
        'keywords': 'الإسماعيلية، دليل، محلات، خدمات، مطاعم، صيدليات',
    }

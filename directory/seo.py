from django.utils.text import slugify
from django.contrib.sites.models import Site

class SEOManager:
    """مدير SEO احترافي"""
    
    @staticmethod
    def get_site_url():
        """الحصول على رابط الموقع"""
        try:
            site = Site.objects.get_current()
            return f"https://{site.domain}"
        except:
            return "https://ismailia-guide.com"
    
    @staticmethod
    def generate_meta_tags(page_type, **kwargs):
        """توليد Meta Tags ديناميكية"""
        
        site_url = SEOManager.get_site_url()
        
        meta = {
            'title': kwargs.get('title', 'دليل الإسماعيلية'),
            'description': kwargs.get('description', 'أشمل دليل إلكتروني للمحلات والخدمات في الإسماعيلية'),
            'keywords': kwargs.get('keywords', 'دليل الإسماعيلية, محلات الإسماعيلية, خدمات الإسماعيلية'),
            'url': kwargs.get('url', site_url),
            'image': kwargs.get('image', f'{site_url}/static/images/logo.png'),
            'site_name': 'دليل الإسماعيلية',
            'type': 'website',
            'locale': 'ar_EG',
        }
        
        # تخصيص حسب نوع الصفحة
        if page_type == 'business':
            business = kwargs.get('business')
            if business:
                meta.update({
                    'title': f"{business.name} - {business.category.name} | دليل الإسماعيلية",
                    'description': business.description[:160] if business.description else f"معلومات عن {business.name} في {business.district.name}",
                    'keywords': f"{business.name}, {business.category.name}, {business.district.name}, الإسماعيلية",
                    'url': f"{site_url}/business/{business.slug}/",
                    'image': business.logo.url if business.logo else meta['image'],
                    'type': 'business.business',
                })
        
        elif page_type == 'category':
            category = kwargs.get('category')
            if category:
                meta.update({
                    'title': f"{category.name} | دليل الإسماعيلية",
                    'description': f"أفضل {category.name} في الإسماعيلية. اكتشف محلات {category.name} بالقرب منك.",
                    'keywords': f"{category.name}, دليل {category.name}, الإسماعيلية",
                })
        
        return meta

from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Business, Category, District

class BusinessSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8
    
    def items(self):
        return Business.objects.filter(is_active=True, is_verified=True)
    
    def lastmod(self, obj):
        return obj.updated_at
    
    def location(self, obj):
        return f'/business/{obj.slug}/'


class CategorySitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.7
    
    def items(self):
        return Category.objects.filter(is_active=True)
    
    def location(self, obj):
        return f'/category/{obj.slug}/'


class StaticViewSitemap(Sitemap):
    priority = 0.5
    changefreq = 'monthly'
    
    def items(self):
        return ['home', 'business_list', 'categories', 'about', 'contact', 'faq']
    
    def location(self, item):
        return reverse(item)

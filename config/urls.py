"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
"""
URL configuration for config project.
"""
"""
URL configuration for config project.
"""
from django.contrib import admin
from django.urls import path, include, register_converter
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap

from directory.sitemaps import BusinessSitemap, CategorySitemap, StaticViewSitemap
from directory.converters import UnicodeSlugConverter

# تسجيل الـ Converter مع حماية من إعادة التحميل ✅
try:
    register_converter(UnicodeSlugConverter, 'uslug')
except ValueError:
    # Converter مسجل بالفعل (بسبب auto-reload)
    pass

# Custom Error Handlers
handler404 = 'directory.views.custom_404'
handler500 = 'directory.views.custom_500'

# تخصيص Admin Panel
admin.site.site_header = 'إدارة دليل الإسماعيلية'
admin.site.site_title = 'دليل الإسماعيلية'
admin.site.index_title = 'لوحة التحكم'

# Sitemaps Configuration
sitemaps = {
    'businesses': BusinessSitemap,
    'categories': CategorySitemap,
    'static': StaticViewSitemap,
}

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('', include('directory.urls')),
    path('products/', include('products.urls')),
    path('subscriptions/', include('subscriptions.urls')),
    path('reviews/', include('reviews.urls')),
    path('payments/', include('payments.urls')),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='sitemap'),
]

# Static & Media Files (Development Only)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

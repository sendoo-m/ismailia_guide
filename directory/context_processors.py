from .models import Category, Governorate, District


from django.conf import settings

def seo_defaults(request):
    """إضافة قيم SEO الافتراضية لكل الصفحات"""
    return {
        'seo': {
            'site_name': getattr(settings, 'SITE_NAME', 'دليل الإسماعيلية'),
            'title': 'دليل الإسماعيلية - دليل شامل للمحلات والخدمات',
            'description': 'دليل شامل للمحلات التجارية والخدمات في الإسماعيلية والمحافظات المجاورة',
            'keywords': 'الإسماعيلية، دليل، محلات، خدمات، مطاعم، صيدليات',

        # الفئات (للـ navbar)
        'navbar_categories': Category.objects.filter(
            is_active=True
        ).order_by('order', 'name')[:8],
        
        # المحافظات (للـ navbar)
        'navbar_governorates': Governorate.objects.filter(
            is_active=True
        ).order_by('order', 'name'),
        
        # إحصائيات
        'total_categories': Category.objects.filter(is_active=True).count(),
        'total_governorates': Governorate.objects.filter(is_active=True).count(),
        'total_districts': District.objects.filter(is_active=True).count(),
    }
        }
from directory.models import Governorate, Business
from django.db.models import Count, Q


def navbar_context(request):
    """
    Context processor لإضافة بيانات الـ Navbar في كل الصفحات
    """
    
    # جلب أول 6 محافظات نشطة مع عدد المحلات
    navbar_governorates = Governorate.objects.filter(
        is_active=True
    ).annotate(
        business_count=Count(
            'district__business',
            filter=Q(
                district__business__is_active=True,
                district__business__is_verified=True
            ),
            distinct=True
        )
    ).order_by('order', 'name')[:6]
    
    # حساب المحلات المعلقة (للـ Staff فقط)
    pending_businesses_count = 0
    pending_reviews_count = 0  # ← صفر مؤقتاً
    
    if request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser):
        pending_businesses_count = Business.objects.filter(is_verified=False).count()
        
        # ← علّق على Reviews مؤقتاً
        # try:
        #     from reviews.models import Review
        #     pending_reviews_count = Review.objects.filter(is_approved=False).count()
        # except Exception:
        #     pending_reviews_count = 0
    
    return {
        'navbar_governorates': navbar_governorates,
        'pending_businesses_count': pending_businesses_count,
        'pending_reviews_count': pending_reviews_count,
    }

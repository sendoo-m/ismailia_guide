from directory.models import Business, Category, Governorate, District
from accounts.views.admin_views import get_admin_stats  # ✅ الـ import الصح


def admin_stats(request):
    """
    Context Processor لعرض الإحصائيات في كل صفحات الـ Dashboard
    """
    
    # لو المستخدم مش مسجل دخول أو مش Admin
    if not request.user.is_authenticated or not (request.user.is_staff or request.user.is_superuser):
        return {}
    
    # إحصائيات المحلات
    total_businesses = Business.objects.count()
    active_businesses = Business.objects.filter(is_active=True).count()
    pending_businesses = Business.objects.filter(is_verified=False).count()
    
    # إحصائيات الفئات
    total_categories = Category.objects.count()
    active_categories = Category.objects.filter(is_active=True).count()
    
    # إحصائيات المحافظات والأحياء
    total_governorates = Governorate.objects.count()
    active_governorates = Governorate.objects.filter(is_active=True).count()
    total_districts = District.objects.count()
    active_districts = District.objects.filter(is_active=True).count()
    
    # إحصائيات التقييمات
    total_reviews = 0
    pending_reviews = 0
    
    try:
        from reviews.models import Review
        total_reviews = Review.objects.count()
        pending_reviews = Review.objects.filter(is_approved=False).count()
    except:
        pass
    
    return {
        'stats': {
            # المحلات
            'total_businesses': total_businesses,
            'active_businesses': active_businesses,
            'pending_businesses': pending_businesses,
            
            # الفئات
            'total_categories': total_categories,
            'active_categories': active_categories,
            
            # المحافظات والأحياء
            'total_governorates': total_governorates,
            'active_governorates': active_governorates,
            'total_districts': total_districts,
            'active_districts': active_districts,
            
            # التقييمات
            'total_reviews': total_reviews,
            'pending_reviews': pending_reviews,
        }
    }

def get_reviews_stats():
    """
    جلب إحصائيات Reviews بشكل آمن
    يرجع أصفار لو الجدول مش موجود
    """
    try:
        from reviews.models import Review
        from django.db import connection
        
        # تحقق من وجود الجدول
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='reviews_review';"
            )
            if not cursor.fetchone():
                return {
                    'total': 0,
                    'approved': 0,
                    'pending': 0
                }
        
        return {
            'total': Review.objects.count(),
            'approved': Review.objects.filter(is_approved=True).count(),
            'pending': Review.objects.filter(is_approved=False).count()
        }
    except Exception:
        return {
            'total': 0,
            'approved': 0,
            'pending': 0
        }

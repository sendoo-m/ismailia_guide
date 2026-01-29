from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q, Count, Avg
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.http import require_GET

# المودلز
from .models import Category, District, Business, Governorate
from products.models import Product
from reviews.models import Review
from .seo import SEOManager


# def home(request):
#     """الصفحة الرئيسية"""
    
#     # الفئات - استخدام related_query_name (business مفرد)
#     categories = Category.objects.filter(
#         is_active=True
#     ).annotate(
#         business_count=Count(
#             'business',  # ✅ related_query_name
#             filter=Q(business__is_active=True, business__is_verified=True)
#         )
#     ).order_by('order', 'name')[:12]
    
#     # المحافظات - استخدام related_query_name (district مفرد)
#     governorates = Governorate.objects.filter(
#         is_active=True
#     ).annotate(
#         district_count=Count(
#             'district',  # ✅ related_query_name
#             filter=Q(district__is_active=True)
#         ),
#         business_count=Count(
#             'district__business',  # ✅ district.business
#             filter=Q(
#                 district__business__is_active=True,
#                 district__business__is_verified=True
#             )
#         )
#     ).order_by('order', 'name')[:6]
    
#     # المحلات المميزة
#     featured_businesses = Business.objects.filter(
#         is_active=True,
#         is_verified=True,
#         is_featured=True,
#     ).select_related(
#         'category', 
#         'district', 
#         'district__governorate'
#     ).order_by('-view_count')[:6]
    
#     # أحدث المحلات
#     latest_businesses = Business.objects.filter(
#         is_active=True,
#         is_verified=True,
#     ).select_related(
#         'category', 
#         'district', 
#         'district__governorate'
#     ).order_by('-created_at')[:6]
    
#     # Meta Tags - SEO ✅
#     try:
#         meta = SEOManager.generate_meta_tags('home')
#     except Exception:
#         # Fallback إذا SEOManager مش شغال
#         meta = {
#             'title': 'دليل الإسماعيلية - دليل شامل للمحلات والخدمات',
#             'description': 'اكتشف أفضل المحلات التجارية والخدمات في الإسماعيلية والمحافظات المجاورة. دليلك الشامل للمطاعم والمقاهي والصيدليات والخدمات الطبية وأكثر.',
#             'keywords': 'الإسماعيلية، دليل الإسماعيلية، محلات، خدمات، مطاعم، صيدليات، مقاهي، خدمات طبية',
#             'site_name': 'دليل الإسماعيلية',
#             'url': request.build_absolute_uri(),
#             'og_type': 'website',
#         }
    
#     context = {
#         'categories': categories,
#         'governorates': governorates,
#         'featured_businesses': featured_businesses,
#         'latest_businesses': latest_businesses,
#         'page_title': 'الرئيسية',
#         'meta': meta,
#     }
    
#     return render(request, 'directory/home.html', context)

# def business_list(request):
#     """قائمة جميع المحلات مع فلاتر"""
#     businesses = Business.objects.filter(
#         is_active=True,
#         is_verified=True,
#     ).select_related('category', 'district', 'district__governorate', 'owner')
    
#     # الفلاتر المتاحة
#     categories = Category.objects.filter(is_active=True).order_by('order', 'name')
#     governorates = Governorate.objects.filter(is_active=True).order_by('order', 'name')
#     districts = District.objects.filter(is_active=True).select_related('governorate').order_by('governorate__name', 'name')
    
#     # البحث النصي
#     query = request.GET.get('q', '')
#     if query:
#         businesses = businesses.filter(
#             Q(name__icontains=query) |
#             Q(description__icontains=query) |
#             Q(address__icontains=query)
#         )
    
#     # فلترة بالفئة
#     selected_category = request.GET.get('category')
#     if selected_category:
#         businesses = businesses.filter(category__slug=selected_category)
    
#     # فلترة بالمحافظة
#     selected_governorate = request.GET.get('governorate')
#     selected_governorate_obj = None
#     if selected_governorate:
#         businesses = businesses.filter(district__governorate__slug=selected_governorate)
#         selected_governorate_obj = governorates.filter(slug=selected_governorate).first()
        
#         # تحديث قائمة الأحياء حسب المحافظة
#         districts = districts.filter(governorate__slug=selected_governorate)
    
#     # فلترة بالحي
#     selected_district = request.GET.get('district')
#     selected_district_obj = None
#     if selected_district:
#         businesses = businesses.filter(district__slug=selected_district)
#         selected_district_obj = districts.filter(slug=selected_district).first()
    
#     # الترتيب
#     order = request.GET.get('order', '-created_at')
#     if order == 'name':
#         businesses = businesses.order_by('name')
#     elif order == '-view_count':
#         businesses = businesses.order_by('-view_count')
#     else:
#         businesses = businesses.order_by('-created_at')
    
#     # Pagination
#     paginator = Paginator(businesses, 12)
#     page = request.GET.get('page')
#     businesses_page = paginator.get_page(page)
        
#     # إضافة Meta Tags ✅
#     meta = SEOManager.generate_meta_tags('business_list')
  
#     context = {
#         'businesses': businesses_page,
#         'categories': categories,
#         'governorates': governorates,
#         'districts': districts,
#         'query': query,
#         'selected_category': selected_category,
#         'selected_governorate': selected_governorate,
#         'selected_governorate_obj': selected_governorate_obj,
#         'selected_district': selected_district,
#         'selected_district_obj': selected_district_obj,
#         'total_count': paginator.count,
#         'order': order,
#         'meta': meta,  # ✅ أضف هذا السطر

#     }
#     return render(request, 'directory/business_list.html', context)
# directory/views.py

# directory/views.py
from django.shortcuts import render
from django.db.models import Q, Avg, Count
from .models import Business, Category, Governorate, District
from .seo import SEOManager


def home(request):
    """الصفحة الرئيسية"""
    
    # الفئات
    categories = Category.objects.filter(
        is_active=True
    ).annotate(
        business_count=Count(
            'business',
            filter=Q(business__is_active=True, business__is_verified=True)
        )
    ).order_by('order', 'name')[:12]
    
    # المحافظات
    governorates = Governorate.objects.filter(
        is_active=True
    ).annotate(
        district_count=Count(
            'district',
            filter=Q(district__is_active=True)
        ),
        business_count=Count(
            'district__business',
            filter=Q(
                district__business__is_active=True,
                district__business__is_verified=True
            )
        )
    ).order_by('order', 'name')[:6]
    
    # ✅ المحلات المميزة - بدون annotate للـ properties الموجودة
    featured_businesses = Business.objects.filter(
        is_active=True,
        is_verified=True,
        is_featured=True,
    ).select_related(
        'category', 
        'district', 
        'district__governorate'
    ).prefetch_related('reviews').order_by('-view_count')[:6]
    
    # ✅ أحدث المحلات - بدون annotate للـ properties الموجودة
    latest_businesses = Business.objects.filter(
        is_active=True,
        is_verified=True,
    ).select_related(
        'category', 
        'district', 
        'district__governorate'
    ).prefetch_related('reviews').order_by('-created_at')[:6]
    
    # Meta Tags - SEO
    try:
        meta = SEOManager.generate_meta_tags('home')
    except Exception:
        meta = {
            'title': 'دليل الإسماعيلية - دليل شامل للمحلات والخدمات',
            'description': 'اكتشف أفضل المحلات التجارية والخدمات في الإسماعيلية والمحافظات المجاورة.',
            'keywords': 'الإسماعيلية، دليل، محلات، خدمات، مطاعم، صيدليات',
            'site_name': 'دليل الإسماعيلية',
            'url': request.build_absolute_uri(),
            'og_type': 'website',
        }
    
    context = {
        'categories': categories,
        'governorates': governorates,
        'featured_businesses': featured_businesses,
        'latest_businesses': latest_businesses,
        'page_title': 'الرئيسية',
        'meta': meta,
    }
    
    return render(request, 'directory/home.html', context)

# directory/views.py

def business_list(request):
    """قائمة المحلات مع البحث والفلتر"""
    
    # ✅ استقبال البحث من الـ Form
    search_query = request.GET.get('q', '').strip()
    category_slug = request.GET.get('category', '')
    governorate_slug = request.GET.get('governorate', '')
    district_slug = request.GET.get('district', '')
    order = request.GET.get('order', '-created_at')
    
    # Base queryset - ✅ بدون annotate للـ properties
    businesses = Business.objects.filter(
        is_active=True,
        is_verified=True
    ).select_related(
        'category', 
        'district', 
        'district__governorate'
    ).prefetch_related('reviews')  # ✅ بدل annotate
    
    # ✅ تطبيق البحث
    if search_query:
        businesses = businesses.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(address__icontains=search_query) |
            Q(category__name__icontains=search_query) |
            Q(district__name__icontains=search_query) |
            Q(district__governorate__name__icontains=search_query)
        )
    
    # فلتر حسب الفئة
    if category_slug:
        businesses = businesses.filter(category__slug=category_slug)
    
    # فلتر حسب المحافظة
    if governorate_slug:
        businesses = businesses.filter(district__governorate__slug=governorate_slug)
    
    # فلتر حسب الحي
    if district_slug:
        businesses = businesses.filter(district__slug=district_slug)
    
    # ترتيب النتائج
    businesses = businesses.order_by('-is_featured', '-is_verified', order)
    
    # Categories & Governorates للفلاتر
    categories = Category.objects.filter(is_active=True).annotate(
        business_count=Count('business', filter=Q(business__is_active=True))
    )
    
    governorates = Governorate.objects.filter(is_active=True).annotate(
        business_count=Count('district__business', filter=Q(district__business__is_active=True))
    )
    
    # Meta Tags
    try:
        meta = SEOManager.generate_meta_tags('business_list', search_query=search_query)
    except Exception:
        meta = {
            'title': f'نتائج البحث عن "{search_query}" - دليل الإسماعيلية' if search_query else 'جميع المحلات - دليل الإسماعيلية',
            'description': 'اكتشف أفضل المحلات والخدمات في الإسماعيلية',
        }
    
    context = {
        'businesses': businesses,
        'categories': categories,
        'governorates': governorates,
        'search_query': search_query,
        'selected_category': category_slug,
        'selected_governorate': governorate_slug,
        'selected_district': district_slug,
        'order': order,
        'total_results': businesses.count(),
        'page_title': f'نتائج البحث عن "{search_query}"' if search_query else 'جميع المحلات',
        'meta': meta,
    }
    
    return render(request, 'directory/business_list.html', context)


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Avg, Count
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Business
from reviews.models import Review
from .seo import SEOManager


def business_detail(request, slug):
    """تفاصيل محل معين + SEO + تقييمات + Pagination"""
    
    business = get_object_or_404(
        Business.objects.select_related('category', 'district', 'district__governorate', 'owner'),
        slug=slug,
        is_active=True,
    )

    # معالجة إضافة تقييم جديد
    if request.method == 'POST' and 'add_review' in request.POST:
        if not request.user.is_authenticated:
            messages.error(request, '❌ يجب تسجيل الدخول أولاً لإضافة تقييم.')
            return redirect('login')
        
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')

        if rating and comment:
            existing_review = Review.objects.filter(business=business, user=request.user).first()
            
            if existing_review:
                messages.warning(request, '⚠️ لقد قمت بتقييم هذا المحل من قبل.')
            else:
                Review.objects.create(
                    business=business,
                    user=request.user,
                    rating=int(rating),
                    comment=comment,
                    is_approved=False,
                )
                messages.success(request, '✅ شكراً لك! تم إرسال تقييمك وسيتم مراجعته قريباً.')
        else:
            messages.error(request, '❌ يرجى إدخال التقييم والتعليق.')

        return redirect('business_detail', slug=slug)

    # زيادة عداد المشاهدات
    business.view_count += 1
    business.save(update_fields=['view_count'])

    # المنتجات
    products = business.products.filter(is_available=True).prefetch_related('images').order_by('order', '-created_at')[:6]

    # التقييمات المعتمدة
    all_reviews = business.reviews.filter(is_approved=True).select_related('user')
    
    # حساب متوسط التقييم
    review_stats = all_reviews.aggregate(avg_rating=Avg('rating'), total_reviews=Count('id'))
    avg_rating = round(review_stats['avg_rating'] or 0, 1)
    total_reviews = review_stats['total_reviews']

    # Pagination للتقييمات
    reviews_list = all_reviews.order_by('-created_at')
    paginator = Paginator(reviews_list, 5)
    page_number = request.GET.get('page', 1)
    
    try:
        reviews = paginator.page(page_number)
    except PageNotAnInteger:
        reviews = paginator.page(1)
    except EmptyPage:
        reviews = paginator.page(paginator.num_pages)

    # الاشتراك
    has_active_subscription = False
    subscription_plan = None
    try:
        from subscriptions.models import Subscription
        subscription = Subscription.objects.filter(business=business, status='active').select_related('plan').first()
        if subscription:
            has_active_subscription = True
            subscription_plan = subscription.plan
    except (ImportError, Exception):
        pass

    # Meta Tags
    meta = SEOManager.generate_meta_tags('business', business=business)

    context = {
        'business': business,
        'products': products,
        'reviews': reviews,
        'avg_rating': avg_rating,
        'total_reviews': total_reviews,
        'has_active_subscription': has_active_subscription,
        'subscription_plan': subscription_plan,
        'meta': meta,
    }
    
    return render(request, 'directory/business_detail.html', context)


def categories_view(request):
    """صفحة عرض جميع الفئات"""
    categories = Category.objects.filter(
        is_active=True
    ).annotate(
        business_count=Count(
            'business',  # ✅ مفرد (related_query_name)
            filter=Q(business__is_active=True, business__is_verified=True)
        )
    ).order_by('order', 'name')
    
    context = {
        'categories': categories,
        'page_title': 'الفئات',
        'page_description': 'تصفح جميع فئات المحلات والخدمات في الإسماعيلية',
    }
    return render(request, 'directory/categories.html', context)


def category_detail(request, slug):
    """عرض محلات فئة معينة"""
    category = get_object_or_404(Category, slug=slug, is_active=True)

    businesses = Business.objects.filter(
        category=category,
        is_active=True,
        is_verified=True,
    ).select_related('district', 'district__governorate')

    district_slug = request.GET.get('district')
    selected_district_name = None
    if district_slug:
        businesses = businesses.filter(district__slug=district_slug)
        district_obj = District.objects.filter(slug=district_slug).first()
        if district_obj:
            selected_district_name = district_obj.name

    order = request.GET.get('order', '-created_at')
    if order == '-created_at':
        businesses = businesses.order_by('-created_at')
    elif order == 'name':
        businesses = businesses.order_by('name')
    elif order == '-view_count':
        businesses = businesses.order_by('-view_count')

    districts = District.objects.filter(
        is_active=True
    ).annotate(
        business_count=Count(
            'business',  # ✅ مفرد (related_query_name)
            filter=Q(
                business__category=category,
                business__is_active=True,
                business__is_verified=True,
            )
        )
    ).filter(business_count__gt=0).order_by('name')

    context = {
        'category': category,
        'businesses': businesses,
        'districts': districts,
        'selected_district': district_slug,
        'selected_district_name': selected_district_name,
    }
    return render(request, 'directory/category_detail.html', context)


def district_detail(request, slug):
    """المحلات حسب حي معين"""
    district = get_object_or_404(
        District.objects.select_related('governorate'),
        slug=slug,
        is_active=True
    )

    businesses = Business.objects.filter(
        district=district,
        is_active=True,
        is_verified=True,
    ).select_related('category', 'district__governorate').order_by('-created_at')

    context = {
        'district': district,
        'businesses': businesses,
    }
    return render(request, 'directory/district_detail.html', context)


def map_view(request):
    """عرض جميع المحلات على الخريطة"""
    businesses = Business.objects.filter(
        is_active=True,
        is_verified=True,
        latitude__isnull=False,
        longitude__isnull=False,
    ).select_related('category', 'district', 'district__governorate')

    context = {
        'businesses': businesses,
    }
    return render(request, 'directory/map_view.html', context)


def contact(request):
    """صفحة اتصل بنا"""
    if request.method == 'POST':
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        # TODO: حفظ الرسالة أو إرسال بريد
        messages.success(request, 'تم إرسال رسالتك بنجاح! سنتواصل معك قريباً.')
        return redirect('contact')

    return render(request, 'directory/contact.html')


def about(request):
    """صفحة عن الدليل"""
    return render(request, 'directory/about.html')


def privacy(request):
    """صفحة سياسة الخصوصية"""
    from django.utils import timezone
    context = {'current_date': timezone.now()}
    return render(request, 'directory/privacy.html', context)


def terms(request):
    """صفحة الشروط والأحكام"""
    from django.utils import timezone
    context = {'current_date': timezone.now()}
    return render(request, 'directory/terms.html', context)


def faq(request):
    """صفحة الأسئلة الشائعة"""
    return render(request, 'directory/faq.html')


def custom_404(request, exception):
    """صفحة 404 مخصصة"""
    return render(request, '404.html', status=404)


def custom_500(request):
    """صفحة 500 مخصصة"""
    return render(request, '500.html', status=500)


@require_GET
def get_districts_by_governorate(request, governorate_id):
    """API لجلب الأحياء حسب المحافظة"""
    try:
        districts = District.objects.filter(
            governorate_id=governorate_id,
            is_active=True
        ).order_by('name').values('id', 'name')
        
        return JsonResponse({
            'success': True,
            'districts': list(districts)
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


def governorates_view(request):
    """عرض جميع المحافظات"""
    governorates = Governorate.objects.filter(
        is_active=True
    ).annotate(
        district_count=Count('district', filter=Q(district__is_active=True)),  # ✅ مفرد
        business_count=Count(
            'district__business',  # ✅ مفرد
            filter=Q(
                district__business__is_active=True,
                district__business__is_verified=True
            )
        )
    ).order_by('order', 'name')
    
    context = {
        'governorates': governorates,
        'page_title': 'المحافظات',
        'page_description': 'تصفح المحلات والخدمات حسب المحافظة',
    }
    return render(request, 'directory/governorates.html', context)


def governorate_detail(request, slug):
    """صفحة تفاصيل المحافظة"""
    from django.db.models import Q, Count
    from django.core.paginator import Paginator
    
    # جلب المحافظة
    governorate = get_object_or_404(Governorate, slug=slug, is_active=True)
    
    # جلب الأحياء النشطة - استخدم business بدل businesses
    districts = governorate.districts.filter(
        is_active=True
    ).annotate(
        business_count=Count(
            'business',  # ← استخدم business (من related_query_name)
            filter=Q(business__is_active=True, business__is_verified=True),
            distinct=True
        )
    ).order_by('name')
    
    # جلب الفئات المتاحة في هذه المحافظة
    categories = Category.objects.filter(
        is_active=True,
        business__district__governorate=governorate,  # ← استخدم business
        business__is_active=True,
        business__is_verified=True
    ).annotate(
        business_count=Count('business', distinct=True)  # ← استخدم business
    ).distinct().order_by('order', 'name')
    
    # الفلترة
    selected_category = request.GET.get('category')
    selected_district = request.GET.get('district')
    search_query = request.GET.get('search', '')
    
    # جلب المحلات
    businesses = Business.objects.filter(
        district__governorate=governorate,
        is_active=True,
        is_verified=True
    ).select_related('category', 'district', 'owner')
    
    # تطبيق الفلاتر
    if selected_category:
        businesses = businesses.filter(category__slug=selected_category)
    
    if selected_district:
        businesses = businesses.filter(district__slug=selected_district)
    
    if search_query:
        businesses = businesses.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(address__icontains=search_query)
        )
    
    # ترتيب المحلات
    order_by = request.GET.get('order', '-created_at')
    if order_by == 'name':
        businesses = businesses.order_by('name')
    elif order_by == 'featured':
        businesses = businesses.order_by('-is_featured', '-created_at')
    else:
        businesses = businesses.order_by('-created_at')
    
    # Pagination
    paginator = Paginator(businesses, 12)  # 12 محل في الصفحة
    page_number = request.GET.get('page')
    businesses_page = paginator.get_page(page_number)
    
    # إحصائيات المحافظة
    total_districts = districts.count()
    total_businesses = businesses.count()
    featured_businesses = businesses.filter(is_featured=True).count()
    
    context = {
        'governorate': governorate,
        'districts': districts,
        'categories': categories,
        'businesses': businesses_page,
        'total_districts': total_districts,
        'total_businesses': total_businesses,
        'featured_businesses': featured_businesses,
        'selected_category': selected_category,
        'selected_district': selected_district,
        'search_query': search_query,
        'order_by': order_by,
        'page_title': governorate.name,
        'page_description': f'اكتشف المحلات والخدمات في {governorate.name} - {total_businesses} محل في {total_districts} حي',
    }
    
    return render(request, 'directory/governorate_detail.html', context)


def districts_view(request):
    """عرض جميع الأحياء"""
    governorate_slug = request.GET.get('governorate')
    selected_governorate = None
    
    districts = District.objects.filter(is_active=True).select_related('governorate')
    
    if governorate_slug:
        districts = districts.filter(governorate__slug=governorate_slug)
        selected_governorate = Governorate.objects.filter(slug=governorate_slug).first()
    
    districts = districts.annotate(
        business_count=Count(
            'business',  # ✅ مفرد (related_query_name)
            filter=Q(business__is_active=True, business__is_verified=True)
        )
    ).order_by('governorate__order', 'governorate__name', 'name')
    
    # المحافظات للفلتر
    governorates = Governorate.objects.filter(is_active=True).order_by('order', 'name')
    
    context = {
        'districts': districts,
        'governorates': governorates,
        'selected_governorate': selected_governorate,
        'page_title': 'الأحياء',
        'page_description': 'تصفح المحلات والخدمات حسب الحي',
    }
    return render(request, 'directory/districts.html', context)


def governorate_districts(request, slug):
    """عرض أحياء محافظة معينة فقط"""
    governorate = get_object_or_404(Governorate, slug=slug, is_active=True)
    
    districts = governorate.districts.filter(
        is_active=True
    ).annotate(
        business_count=Count(
            'business',  # ✅ مفرد (related_query_name)
            filter=Q(business__is_active=True, business__is_verified=True)
        )
    ).order_by('name')
    
    context = {
        'governorate': governorate,
        'districts': districts,
        'page_title': f'أحياء {governorate.name}',
    }
    return render(request, 'directory/governorate_districts.html', context)

def district_detail(request, slug):
    """صفحة تفاصيل حي معين"""
    district = get_object_or_404(District, slug=slug, is_active=True)
    
    # جلب المحلات النشطة في هذا الحي
    businesses = Business.objects.filter(
        district=district,
        is_active=True,
        is_verified=True
    ).select_related('category', 'district').order_by('-created_at')
    
    # Filters
    selected_category = request.GET.get('category', '')
    search_query = request.GET.get('search', '')
    
    if selected_category:
        businesses = businesses.filter(category_id=selected_category)
    
    if search_query:
        businesses = businesses.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(businesses, 12)
    page_number = request.GET.get('page')
    businesses_page = paginator.get_page(page_number)
    
    # ✅ جلب الفئات المتاحة في هذا الحي (مصحح)
    categories = Category.objects.filter(
        business__district=district,  # ← استخدم business مش businesses
        business__is_active=True,
        is_active=True
    ).distinct().order_by('name')
    
    # أحياء أخرى في نفس المحافظة
    other_districts = District.objects.filter(
        governorate=district.governorate,
        is_active=True
    ).exclude(id=district.id).annotate(
        business_count=Count('business')  # ← استخدم business مش businesses
    ).order_by('order', 'name')[:6]
    
    context = {
        'district': district,
        'businesses': businesses_page,
        'categories': categories,
        'selected_category': selected_category,
        'search_query': search_query,
        'other_districts': other_districts,
    }
    
    return render(request, 'directory/district_detail.html', context)

def governorates(request):
    """صفحة قائمة المحافظات"""
    
    # جلب جميع المحافظات النشطة مع الإحصائيات
    governorates_list = Governorate.objects.filter(
        is_active=True
    ).annotate(
        # عدد الأحياء
        district_count=Count('district', filter=Q(district__is_active=True), distinct=True),
        
        # عدد المحلات
        business_count=Count(
            'district__business',
            filter=Q(district__business__is_active=True, district__business__is_verified=True),
            distinct=True
        ),
        
        # عدد الفئات المتاحة
        category_count=Count(
            'district__business__category',
            filter=Q(district__business__is_active=True, district__business__is_verified=True),
            distinct=True
        )
    ).order_by('order', 'name')
    
    # Filter (اختياري)
    search_query = request.GET.get('search', '')
    if search_query:
        governorates_list = governorates_list.filter(
            Q(name__icontains=search_query) |
            Q(name_en__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # إحصائيات عامة
    total_governorates = governorates_list.count()
    total_businesses = Business.objects.filter(is_active=True, is_verified=True).count()
    total_districts = District.objects.filter(is_active=True).count()
    total_categories = Category.objects.filter(is_active=True).count()
    
    context = {
        'governorates': governorates_list,
        'total_governorates': total_governorates,
        'total_businesses': total_businesses,
        'total_districts': total_districts,
        'total_categories': total_categories,
        'search_query': search_query,
    }
    
    return render(request, 'directory/governorates.html', context)

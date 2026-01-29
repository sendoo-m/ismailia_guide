"""
Admin Views
===========
لوحة تحكم الإدارة وإدارة المحلات والفئات والتقييمات
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Q, Count, Avg
from django.core.paginator import Paginator
from django.contrib.auth import get_user_model

from directory.models import Business, Category, Governorate, District
from products.models import Product
from reviews.models import Review
from subscriptions.models import SubscriptionPlan, Subscription

User = get_user_model()


# ============================================
# Helper Functions
# ============================================

def is_staff_or_superuser(user):
    """التحقق من صلاحيات المسؤول"""
    return user.is_staff or user.is_superuser


# def get_admin_stats():
#     """إحصائيات للـ Sidebar"""
#     return {
#         'total_businesses': Business.objects.count(),
#         'pending_businesses': Business.objects.filter(is_verified=False).count(),
#         'total_categories': Category.objects.count(),
#         'total_governorates': Governorate.objects.count(),
#         'pending_reviews': Review.objects.filter(is_approved=False).count(),
#     }
def get_admin_stats():
    """إحصائيات للـ Sidebar وكل الصفحات"""
    
    # إحصائيات التقييمات
    try:
        from reviews.models import Review
        total_reviews = Review.objects.count()
        pending_reviews = Review.objects.filter(is_approved=False).count()
    except ImportError:
        total_reviews = 0
        pending_reviews = 0
    
    return {
        # ✅ المحلات
        'total_businesses': Business.objects.count(),
        'active_businesses': Business.objects.filter(is_active=True, is_verified=True).count(),
        'pending_businesses': Business.objects.filter(is_verified=False).count(),
        
        # ✅ الفئات
        'total_categories': Category.objects.count(),
        'active_categories': Category.objects.filter(is_active=True).count(),
        
        # ✅ المحافظات (كانت ناقصة!)
        'total_governorates': Governorate.objects.count(),
        'active_governorates': Governorate.objects.filter(is_active=True).count(),
        
        # ✅ الأحياء (كانت ناقصة!)
        'total_districts': District.objects.count(),
        'active_districts': District.objects.filter(is_active=True).count(),
        
        # ✅ التقييمات
        'total_reviews': total_reviews,
        'pending_reviews': pending_reviews,
    }


# ============================================
# Admin Dashboard
# ============================================

@login_required
@user_passes_test(is_staff_or_superuser)
def admin_dashboard(request):
    """لوحة تحكم الإدارة"""
    
    # إحصائيات المحلات
    total_businesses = Business.objects.count()
    active_businesses = Business.objects.filter(is_active=True).count()
    pending_businesses = Business.objects.filter(is_verified=False).count()
    featured_businesses = Business.objects.filter(is_featured=True).count()
    
    # إحصائيات الفئات والمحافظات
    total_categories = Category.objects.count()
    active_categories = Category.objects.filter(is_active=True).count()
    total_governorates = Governorate.objects.count()
    active_governorates = Governorate.objects.filter(is_active=True).count()
    total_districts = District.objects.count()
    active_districts = District.objects.filter(is_active=True).count()
    
    # إحصائيات المستخدمين
    total_users = User.objects.count()
    active_users = User.objects.filter(is_active=True).count()
    staff_users = User.objects.filter(is_staff=True).count()
    
    # إحصائيات التقييمات
    total_reviews = Review.objects.count()
    approved_reviews = Review.objects.filter(is_approved=True).count()
    pending_reviews = Review.objects.filter(is_approved=False).count()
    
    # أحدث التقييمات
    latest_reviews = Review.objects.select_related(
        'business', 'user'
    ).order_by('-created_at')[:5]
    
    # أحدث المحلات
    latest_businesses = Business.objects.select_related(
        'category', 'district', 'owner'
    ).order_by('-created_at')[:5]
    
    # المحلات المعلقة
    pending_businesses_list = Business.objects.filter(
        is_verified=False
    ).select_related('category', 'district', 'owner').order_by('-created_at')[:5]
    
    # أكثر الفئات استخداماً
    top_categories = Category.objects.annotate(
        business_count=Count('business')
    ).order_by('-business_count')[:5]
    
    # أكثر المحافظات نشاطاً
    top_governorates = Governorate.objects.annotate(
        business_count=Count('district__business', distinct=True)
    ).order_by('-business_count')[:5]
    
    stats = {
        'total_businesses': total_businesses,
        'active_businesses': active_businesses,
        'pending_businesses': pending_businesses,
        'total_reviews': total_reviews,
        'pending_reviews': pending_reviews,
    }
    
    context = {
        'total_businesses': total_businesses,
        'active_businesses': active_businesses,
        'pending_businesses': pending_businesses,
        'featured_businesses': featured_businesses,
        'total_categories': total_categories,
        'active_categories': active_categories,
        'total_governorates': total_governorates,
        'active_governorates': active_governorates,
        'total_districts': total_districts,
        'active_districts': active_districts,
        'total_users': total_users,
        'active_users': active_users,
        'staff_users': staff_users,
        'total_reviews': total_reviews,
        'approved_reviews': approved_reviews,
        'pending_reviews': pending_reviews,
        'latest_businesses': latest_businesses,
        'pending_businesses_list': pending_businesses_list,
        'latest_reviews': latest_reviews,
        'top_categories': top_categories,
        'top_governorates': top_governorates,
        'stats': stats,
        'page_title': 'لوحة التحكم',
    }
    
    return render(request, 'accounts/dashboard.html', context)


# ============================================
# Manage Businesses
# ============================================

@login_required
@user_passes_test(is_staff_or_superuser)
def manage_businesses(request):
    """إدارة المحلات - للإدارة فقط"""
    
    # الفلترة
    status_filter = request.GET.get('status', 'all')
    search_query = request.GET.get('search', '')
    category_filter = request.GET.get('category')
    governorate_filter = request.GET.get('governorate')
    
    # جلب المحلات
    businesses = Business.objects.select_related(
        'category', 
        'district', 
        'district__governorate',
        'owner'
    )
    
    # تطبيق فلاتر الحالة
    if status_filter == 'active':
        businesses = businesses.filter(is_active=True, is_verified=True)
    elif status_filter == 'pending':
        businesses = businesses.filter(is_verified=False)
    elif status_filter == 'inactive':
        businesses = businesses.filter(is_active=False)
    elif status_filter == 'featured':
        businesses = businesses.filter(is_featured=True)
    
    # البحث
    if search_query:
        businesses = businesses.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(address__icontains=search_query) |
            Q(phone__icontains=search_query) |
            Q(owner__username__icontains=search_query) |
            Q(owner__email__icontains=search_query)
        )
    
    # فلترة بالفئة
    if category_filter:
        businesses = businesses.filter(category__slug=category_filter)
    
    # فلترة بالمحافظة
    if governorate_filter:
        businesses = businesses.filter(district__governorate__slug=governorate_filter)
    
    # الترتيب
    order_by = request.GET.get('order', '-created_at')
    businesses = businesses.order_by(order_by)
    
    # Pagination
    paginator = Paginator(businesses, 20)
    page_number = request.GET.get('page')
    businesses_page = paginator.get_page(page_number)
    
    # إحصائيات
    total_count = Business.objects.count()
    active_count = Business.objects.filter(is_active=True, is_verified=True).count()
    pending_count = Business.objects.filter(is_verified=False).count()
    inactive_count = Business.objects.filter(is_active=False).count()
    featured_count = Business.objects.filter(is_featured=True).count()
    
    # للفلاتر
    categories = Category.objects.filter(is_active=True).order_by('name')
    governorates = Governorate.objects.filter(is_active=True).order_by('name')
    
    context = {
        'businesses': businesses_page,
        'total_count': total_count,
        'active_count': active_count,
        'pending_count': pending_count,
        'inactive_count': inactive_count,
        'featured_count': featured_count,
        'status_filter': status_filter,
        'search_query': search_query,
        'category_filter': category_filter,
        'governorate_filter': governorate_filter,
        'order_by': order_by,
        'categories': categories,
        'governorates': governorates,
        'page_title': 'إدارة المحلات',
    }
    
    return render(request, 'accounts/manage_businesses.html', context)


@login_required
@user_passes_test(is_staff_or_superuser)
def toggle_business_status(request, pk):
    """تفعيل/إيقاف محل"""
    business = get_object_or_404(Business, pk=pk)
    business.is_active = not business.is_active
    business.save()
    
    status = "تم تفعيل" if business.is_active else "تم إيقاف"
    messages.success(request, f'{status} محل "{business.name}" بنجاح!')
    
    return redirect('manage_businesses')


@login_required
@user_passes_test(is_staff_or_superuser)
def toggle_business_verification(request, pk):
    """توثيق/إلغاء توثيق محل"""
    business = get_object_or_404(Business, pk=pk)
    business.is_verified = not business.is_verified
    business.save()
    
    status = "تم توثيق" if business.is_verified else "تم إلغاء توثيق"
    messages.success(request, f'{status} محل "{business.name}" بنجاح!')
    
    return redirect('manage_businesses')


@login_required
@user_passes_test(is_staff_or_superuser)
def delete_business_admin(request, pk):
    """حذف محل (للمسؤولين فقط)"""
    business = get_object_or_404(Business, pk=pk)
    
    if request.method == 'POST':
        business_name = business.name
        business.delete()
        messages.success(request, f'تم حذف محل "{business_name}" بنجاح!')
        return redirect('manage_businesses')
    
    context = {'business': business}
    return render(request, 'accounts/delete_business_confirm.html', context)


# ============================================
# Manage Categories
# ============================================

@login_required
@user_passes_test(is_staff_or_superuser)
def manage_categories(request):
    """إدارة الفئات"""
    
    categories = Category.objects.annotate(
        business_count=Count('business')
    ).order_by('-business_count')
    
    # إضافة فئة جديدة
    if request.method == 'POST' and 'add_category' in request.POST:
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        icon = request.POST.get('icon', '')
        order = request.POST.get('order', 0)
        
        if name:
            Category.objects.create(
                name=name,
                description=description,
                icon=icon,
                order=order,
                is_active=True,
            )
            messages.success(request, f'تم إضافة الفئة "{name}" بنجاح!')
            return redirect('manage_categories')
    
    # تعديل فئة
    if request.method == 'POST' and 'edit_category' in request.POST:
        category_id = request.POST.get('category_id')
        category = get_object_or_404(Category, id=category_id)
        
        category.name = request.POST.get('name')
        category.description = request.POST.get('description', '')
        category.icon = request.POST.get('icon', '')
        category.order = request.POST.get('order', 0)
        category.is_active = request.POST.get('is_active') == 'on'
        category.save()
        
        messages.success(request, f'تم تحديث الفئة "{category.name}" بنجاح!')
        return redirect('manage_categories')
    
    # حذف فئة
    if request.method == 'POST' and 'delete_category' in request.POST:
        category_id = request.POST.get('category_id')
        category = get_object_or_404(Category, id=category_id)
        category_name = category.name
        category.delete()
        
        messages.success(request, f'تم حذف الفئة "{category_name}" بنجاح!')
        return redirect('manage_categories')
    
    context = {
        'categories': categories,
        'stats': get_admin_stats(),
    }
    return render(request, 'accounts/manage_categories.html', context)


@login_required
@user_passes_test(is_staff_or_superuser)
def add_category(request):
    """إضافة فئة جديدة"""
    if request.method == 'POST':
        name = request.POST.get('name')
        icon = request.POST.get('icon', 'fa-store')
        description = request.POST.get('description', '')
        order = request.POST.get('order', 0)
        
        Category.objects.create(
            name=name,
            icon=icon,
            description=description,
            order=order,
            is_active=True
        )
        
        messages.success(request, f'تم إضافة فئة "{name}" بنجاح!')
        return redirect('manage_categories')
    
    return render(request, 'accounts/add_category.html')


@login_required
@user_passes_test(is_staff_or_superuser)
def edit_category(request, pk):
    """تعديل فئة"""
    category = get_object_or_404(Category, pk=pk)
    
    if request.method == 'POST':
        category.name = request.POST.get('name')
        category.icon = request.POST.get('icon')
        category.description = request.POST.get('description', '')
        category.order = request.POST.get('order', 0)
        category.is_active = request.POST.get('is_active') == 'on'
        category.save()
        
        messages.success(request, f'تم تحديث فئة "{category.name}" بنجاح!')
        return redirect('manage_categories')
    
    context = {'category': category}
    return render(request, 'accounts/edit_category.html', context)


@login_required
@user_passes_test(is_staff_or_superuser)
def delete_category(request, pk):
    """حذف فئة"""
    category = get_object_or_404(Category, pk=pk)
    
    if category.businesses.exists():
        messages.error(request, f'لا يمكن حذف الفئة "{category.name}" لأنها تحتوي على محلات!')
        return redirect('manage_categories')
    
    if request.method == 'POST':
        category_name = category.name
        category.delete()
        messages.success(request, f'تم حذف فئة "{category_name}" بنجاح!')
        return redirect('manage_categories')
    
    context = {'category': category}
    return render(request, 'accounts/delete_category_confirm.html', context)


# ============================================
# Manage Reviews
# ============================================

@login_required
@user_passes_test(is_staff_or_superuser)
def manage_reviews(request):
    """إدارة التقييمات مع Pagination"""
    
    reviews = Review.objects.select_related(
        'business', 'user'
    ).order_by('-created_at')
    
    # Filter
    status = request.GET.get('status')
    if status == 'pending':
        reviews = reviews.filter(is_approved=False)
    elif status == 'verified':
        reviews = reviews.filter(is_approved=True)
    
    # Pagination
    paginator = Paginator(reviews, 10)
    page_number = request.GET.get('page')
    reviews_page = paginator.get_page(page_number)
    
    context = {
        'reviews': reviews_page,
        'total_count': paginator.count,
        'pending_count': Review.objects.filter(is_approved=False).count(),
        'current_status': status,
    }
    
    return render(request, 'accounts/manage_reviews.html', context)


@login_required
@user_passes_test(is_staff_or_superuser)
def approve_review(request, pk):
    """الموافقة على تقييم"""
    review = get_object_or_404(Review, pk=pk)
    review.is_approved = True
    review.save()
    messages.success(request, f'✅ تمت الموافقة على تقييم {review.reviewer_name}')
    return redirect('manage_reviews')


@login_required
@user_passes_test(is_staff_or_superuser)
def delete_review(request, pk):
    """حذف تقييم"""
    review = get_object_or_404(Review, pk=pk)
    
    if request.method == 'POST' or request.method == 'GET':
        review_name = review.reviewer_name
        business_name = review.business.name
        review.delete()
        messages.success(request, f'✅ تم حذف تقييم {review_name} على {business_name}')
    
    return redirect('manage_reviews')


# ============================================
# Manage Governorates & Districts
# ============================================
@login_required
@user_passes_test(is_staff_or_superuser)
def manage_governorates(request):
    """إدارة المحافظات"""
    
    # جلب المحافظات مع الإحصائيات
    governorates = Governorate.objects.annotate(
        business_count=Count('district__business', distinct=True),
        district_count=Count('district', distinct=True),
        active_business_count=Count(
            'district__business',
            filter=Q(district__business__is_active=True, district__business__is_verified=True),
            distinct=True
        )
    ).order_by('name')
    
    # الإحصائيات العامة
    stats = get_admin_stats()
    
    # معالجة الطلبات POST
    if request.method == 'POST':
        # إضافة محافظة
        if 'add_governorate' in request.POST:
            name = request.POST.get('name')
            name_en = request.POST.get('name_en', '')
            description = request.POST.get('description', '')
            icon = request.POST.get('icon', 'fas fa-city')
            order = request.POST.get('order', 0)
            
            if name:
                Governorate.objects.create(
                    name=name,
                    name_en=name_en,
                    description=description,
                    icon=icon,
                    order=order,
                    is_active=True
                )
                messages.success(request, f'✅ تم إضافة المحافظة "{name}" بنجاح!')
                return redirect('manage_governorates')
        
        # تعديل محافظة
        elif 'edit_governorate' in request.POST:
            governorate_id = request.POST.get('governorate_id')
            governorate = get_object_or_404(Governorate, id=governorate_id)
            
            governorate.name = request.POST.get('name')
            governorate.name_en = request.POST.get('name_en', '')
            governorate.description = request.POST.get('description', '')
            governorate.icon = request.POST.get('icon', 'fas fa-city')
            governorate.order = request.POST.get('order', 0)
            governorate.is_active = request.POST.get('is_active') == 'on'
            
            if 'image' in request.FILES:
                governorate.image = request.FILES['image']
            
            governorate.save()
            messages.success(request, f'✅ تم تحديث المحافظة "{governorate.name}" بنجاح!')
            return redirect('manage_governorates')
        
        # تبديل الحالة
        elif 'toggle_active' in request.POST:
            governorate_id = request.POST.get('governorate_id')
            governorate = get_object_or_404(Governorate, id=governorate_id)
            governorate.is_active = not governorate.is_active
            governorate.save()
            
            status = 'تفعيل' if governorate.is_active else 'إلغاء تفعيل'
            messages.success(request, f'✅ تم {status} المحافظة "{governorate.name}"')
            return redirect('manage_governorates')
        
        # حذف محافظة
        elif 'delete_governorate' in request.POST:
            governorate_id = request.POST.get('governorate_id')
            governorate = get_object_or_404(Governorate, id=governorate_id)
            
            # التحقق من عدم وجود محلات
            business_count = Business.objects.filter(district__governorate=governorate).count()
            
            if business_count > 0:
                messages.error(request, f'❌ لا يمكن حذف المحافظة "{governorate.name}" لأنها تحتوي على {business_count} محل!')
            else:
                governorate_name = governorate.name
                governorate.delete()
                messages.success(request, f'✅ تم حذف المحافظة "{governorate_name}" بنجاح!')
            
            return redirect('manage_governorates')
    
    # السياق
    context = {
        'governorates': governorates,
        
        # الإحصائيات المباشرة
        'total_governorates': stats['total_governorates'],
        'active_governorates': stats['active_governorates'],
        'total_businesses': stats['total_businesses'],
        'total_districts': stats['total_districts'],
        
        # للـ Sidebar
        'stats': stats,
    }
    
    return render(request, 'accounts/manage_governorates.html', context)

@login_required
@user_passes_test(is_staff_or_superuser)
def manage_districts(request):
    """إدارة الأحياء"""
    from directory.models import Business
    
    # Filters - نحتاجهم في البداية
    governorate_filter = request.GET.get('governorate', '')
    search_query = request.GET.get('search', '')
    
    # معالجة POST Requests
    if request.method == 'POST':
        
        # ➕ إضافة حي جديد
        if 'add_district' in request.POST:
            governorate_id = request.POST.get('governorate')
            name = request.POST.get('name')
            description = request.POST.get('description', '')
            order = request.POST.get('order', 0)
            
            if governorate_id and name:
                governorate = get_object_or_404(Governorate, id=governorate_id)
                
                if District.objects.filter(governorate=governorate, name=name).exists():
                    messages.error(request, f'❌ الحي "{name}" موجود بالفعل في {governorate.name}!')
                else:
                    District.objects.create(
                        governorate=governorate,
                        name=name,
                        description=description,
                        order=int(order) if order else 0,
                        is_active=True,
                    )
                    messages.success(request, f'✅ تم إضافة الحي "{name}" بنجاح!')
            else:
                messages.error(request, '❌ يرجى إدخال المحافظة واسم الحي.')
            return redirect('manage_districts')
        
        # ✏️ تعديل حي
        elif 'edit_district' in request.POST:
            district_id = request.POST.get('district_id')
            district = get_object_or_404(District, id=district_id)
            
            district.governorate_id = request.POST.get('governorate')
            district.name = request.POST.get('name')
            district.description = request.POST.get('description', '')
            order = request.POST.get('order', 0)
            district.order = int(order) if order else 0
            district.is_active = request.POST.get('is_active') == 'on'
            district.save()
            
            messages.success(request, f'✅ تم تحديث الحي "{district.name}" بنجاح!')
            return redirect('manage_districts')
        
        # 🗑️ حذف حي
        elif 'delete_district' in request.POST:
            district_id = request.POST.get('district_id')
            district = get_object_or_404(District, id=district_id)
            
            # عدّ المحلات المرتبطة
            business_count = Business.objects.filter(district=district).count()
            
            if business_count > 0:
                messages.error(
                    request, 
                    f'❌ لا يمكن حذف الحي "{district.name}" لأنه يحتوي على {business_count} محل.'
                )
            else:
                district_name = district.name
                district.delete()
                messages.success(request, f'✅ تم حذف الحي "{district_name}" بنجاح!')
            
            return redirect('manage_districts')
        
        # 🔄 تبديل حالة التفعيل
        elif 'toggle_active' in request.POST or request.POST.get('district_id'):
            district_id = request.POST.get('district_id')
            
            if district_id:
                district = get_object_or_404(District, id=district_id)
                
                # عكس الحالة
                district.is_active = not district.is_active
                district.save(update_fields=['is_active'])
                
                # رسالة نجاح
                if district.is_active:
                    messages.success(request, f'✅ تم تفعيل الحي "{district.name}" بنجاح!')
                else:
                    messages.warning(request, f'⚠️ تم إلغاء تفعيل الحي "{district.name}"')
            else:
                messages.error(request, '❌ حدث خطأ! لم يتم تحديد الحي.')
            
            return redirect('manage_districts')
    
    # جلب جميع الأحياء مع الإحصائيات
    districts = District.objects.select_related('governorate').annotate(
        business_count=Count('business', distinct=True),
        active_business_count=Count(
            'business',
            filter=Q(business__is_active=True, business__is_verified=True),
            distinct=True
        )
    ).order_by('governorate__name', 'order', 'name')
    
    # تطبيق الفلاتر
    if governorate_filter:
        districts = districts.filter(governorate_id=governorate_filter)
    
    if search_query:
        districts = districts.filter(
            Q(name__icontains=search_query) |
            Q(governorate__name__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(districts, 15)
    page_number = request.GET.get('page')
    districts_page = paginator.get_page(page_number)
    
    # للـ Filters
    governorates = Governorate.objects.filter(is_active=True).order_by('order', 'name')
    
    # إحصائيات عامة
    total_districts = District.objects.count()
    active_districts = District.objects.filter(is_active=True).count()
    
    context = {
        'districts': districts_page,
        'governorates': governorates,
        'total_districts': total_districts,
        'active_districts': active_districts,
        'current_governorate': governorate_filter,
        'search_query': search_query,
    }
    return render(request, 'accounts/manage_districts.html', context)


# ============================================
# Settings & Vendors Management
# ============================================

@login_required
def settings(request):
    """إعدادات الحساب"""
    user = request.user
    is_admin = user.is_staff or user.is_superuser
    
    if request.method == 'POST':
        form_type = request.POST.get('form_type', '')
        
        if form_type == 'account':
            user.first_name = request.POST.get('first_name', '')
            user.last_name = request.POST.get('last_name', '')
            user.email = request.POST.get('email', user.email)
            user.phone = request.POST.get('phone', '')
            
            try:
                user.save()
                messages.success(request, '✅ تم تحديث المعلومات الشخصية بنجاح!')
            except Exception as e:
                messages.error(request, f'❌ حدث خطأ: {str(e)}')
            
        elif form_type == 'password':
            new_password = request.POST.get('new_password', '')
            confirm_password = request.POST.get('confirm_password', '')
            
            if new_password and confirm_password:
                if new_password == confirm_password:
                    try:
                        user.set_password(new_password)
                        user.save()
                        messages.success(request, '✅ تم تحديث كلمة المرور بنجاح!')
                        from django.contrib.auth import update_session_auth_hash
                        update_session_auth_hash(request, user)
                    except Exception as e:
                        messages.error(request, f'❌ حدث خطأ: {str(e)}')
                else:
                    messages.error(request, '❌ كلمة المرور غير متطابقة!')
            else:
                messages.warning(request, '⚠️ الرجاء إدخال كلمة المرور في الحقلين!')
        
        return redirect('dashboard_settings')
    
    vendors = []
    if is_admin:
        vendors = User.objects.filter(
            user_type='vendor'
        ).prefetch_related('businesses').order_by('-date_joined')
    
    context = {
        'user': user,
        'is_admin': is_admin,
        'vendors': vendors,
    }
    
    return render(request, 'accounts/settings.html', context)


@login_required
@user_passes_test(is_staff_or_superuser)
def add_vendor(request):
    """إضافة صاحب محل جديد"""
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        phone = request.POST.get('phone', '')
        is_active = 'is_active' in request.POST
        
        # التحقق من صحة البيانات
        if password != confirm_password:
            messages.error(request, '❌ كلمة المرور غير متطابقة!')
            return redirect('add_vendor')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, '❌ اسم المستخدم موجود بالفعل!')
            return redirect('add_vendor')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, '❌ البريد الإلكتروني مسجل بالفعل!')
            return redirect('add_vendor')
        
        try:
            # إنشاء المستخدم
            vendor = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                phone=phone,
                user_type='vendor',
                is_active=is_active,
            )
            
            # رفع الصورة (إن وجدت)
            if 'profile_image' in request.FILES:
                vendor.profile_image = request.FILES['profile_image']
                vendor.save()
            
            messages.success(request, f'✅ تم إضافة صاحب المحل "{vendor.get_full_name()}" بنجاح!')
            return redirect('dashboard_settings')
            
        except Exception as e:
            messages.error(request, f'❌ حدث خطأ: {str(e)}')
            return redirect('add_vendor')
    
    context = {
        'stats': get_admin_stats(),
    }
    return render(request, 'accounts/add_vendor.html', context)


@login_required
@user_passes_test(is_staff_or_superuser)
def edit_vendor(request, pk):
    """تعديل صاحب محل"""
    vendor = get_object_or_404(User, pk=pk, user_type='vendor')
    
    if request.method == 'POST':
        vendor.first_name = request.POST.get('first_name')
        vendor.last_name = request.POST.get('last_name')
        vendor.email = request.POST.get('email')
        vendor.phone = request.POST.get('phone', '')
        vendor.is_active = 'is_active' in request.POST
        
        # تحديث كلمة المرور (اختياري)
        new_password = request.POST.get('new_password', '')
        confirm_password = request.POST.get('confirm_password', '')
        
        if new_password and confirm_password:
            if new_password == confirm_password:
                vendor.set_password(new_password)
            else:
                messages.error(request, '❌ كلمة المرور غير متطابقة!')
                return redirect('edit_vendor', pk=pk)
        
        # رفع الصورة (إن وجدت)
        if 'profile_image' in request.FILES:
            vendor.profile_image = request.FILES['profile_image']
        
        try:
            vendor.save()
            messages.success(request, f'✅ تم تحديث بيانات "{vendor.get_full_name()}" بنجاح!')
            return redirect('dashboard_settings')
        except Exception as e:
            messages.error(request, f'❌ حدث خطأ: {str(e)}')
    
    context = {
        'vendor': vendor,
        'stats': get_admin_stats(),
    }
    return render(request, 'accounts/edit_vendor.html', context)


@login_required
@user_passes_test(is_staff_or_superuser)
def delete_vendor(request, pk):
    """حذف صاحب محل"""
    vendor = get_object_or_404(User, pk=pk, user_type='vendor')
    
    if request.method == 'POST':
        vendor_name = vendor.get_full_name()
        vendor.delete()
        messages.success(request, f'✅ تم حذف صاحب المحل "{vendor_name}" بنجاح!')
        return redirect('dashboard_settings')
    
    context = {
        'vendor': vendor,
        'stats': get_admin_stats(),
    }
    return render(request, 'accounts/delete_vendor_confirm.html', context)


@login_required
@user_passes_test(is_staff_or_superuser)
def toggle_vendor_status(request, pk):
    """تفعيل/تعطيل صاحب محل"""
    vendor = get_object_or_404(User, pk=pk, user_type='vendor')
    vendor.is_active = not vendor.is_active
    vendor.save()
    
    status = 'تفعيل' if vendor.is_active else 'إلغاء تفعيل'
    messages.success(request, f'✅ تم {status} حساب "{vendor.get_full_name()}"')
    return redirect('dashboard_settings')

@login_required
@user_passes_test(is_staff_or_superuser)
def manage_users(request):
    """إدارة المستخدمين"""
    
    # Filters
    search_query = request.GET.get('search', '')
    user_type_filter = request.GET.get('user_type', '')
    status_filter = request.GET.get('status', '')
    
    # جلب المستخدمين
    users = User.objects.prefetch_related('businesses').order_by('-date_joined')
    
    # تطبيق الفلاتر
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query)
        )
    
    if user_type_filter:
        if user_type_filter == 'vendor':
            users = users.filter(user_type='vendor')
        elif user_type_filter == 'customer':
            users = users.filter(user_type='customer')
    
    if status_filter:
        if status_filter == 'active':
            users = users.filter(is_active=True)
        elif status_filter == 'inactive':
            users = users.filter(is_active=False)
    
    # Pagination
    paginator = Paginator(users, 10)
    page_number = request.GET.get('page')
    users_page = paginator.get_page(page_number)
    
    # الإحصائيات
    total_users = User.objects.count()
    active_users = User.objects.filter(is_active=True).count()
    vendor_users = User.objects.filter(user_type='vendor').count()
    admin_users = User.objects.filter(is_staff=True).count()
    
    context = {
        'users': users_page,
        'total_users': total_users,
        'active_users': active_users,
        'vendor_users': vendor_users,
        'admin_users': admin_users,
        'search_query': search_query,
        'user_type_filter': user_type_filter,
        'status_filter': status_filter,
        'stats': get_admin_stats(),
    }
    
    return render(request, 'accounts/manage_users.html', context)

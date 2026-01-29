from urllib import request
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout, get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count, Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import transaction
from datetime import timedelta
import csv
from io import TextIOWrapper
from django.db.models import Sum, Count, Q, Avg
from accounts.models import User
from products.models import Product
from reviews.models import Review
from subscriptions.models import SubscriptionPlan, Subscription
from .forms import BusinessForm
from directory.forms import BusinessForm
from directory.models import Business, Category, Governorate, District

# استخدام Custom User Model
User = get_user_model()  # ← مهم جداً!

# ============================================
# HELPER FUNCTIONS - دوال مساعدة
# ============================================

def is_staff_or_superuser(user):
    """التحقق من صلاحيات المسؤول"""
    return user.is_staff or user.is_superuser

# ============================================
# AUTHENTICATION - المصادقة وتسجيل الدخول
# ============================================

def user_login(request):
    """تسجيل الدخول"""
    if request.user.is_authenticated:
        if request.user.is_staff or request.user.is_superuser:
            return redirect('admin_dashboard')
        return redirect('vendor_dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'أهلاً بك، {user.get_full_name() or user.username}! 👋')
            
            # توجيه حسب نوع المستخدم
            if user.is_staff or user.is_superuser:
                return redirect('admin_dashboard')
            elif hasattr(user, 'user_type') and user.user_type == 'vendor':
                return redirect('vendor_dashboard')
            else:
                return redirect('home')
        else:
            messages.error(request, 'اسم المستخدم أو كلمة المرور غير صحيحة!')
    
    return render(request, 'accounts/login.html')

def get_admin_stats():
    return {
        'total_businesses': Business.objects.count(),
        'pending_businesses': Business.objects.filter(is_active=False).count(),
        'total_categories': Category.objects.count(),
        'total_governorates': Governorate.objects.count(),
        'pending_reviews': Review.objects.filter(is_approved=False).count(),
    }


def user_register(request):
    """تسجيل مستخدم جديد - يوجه إلى تسجيل البائع"""
    return register_vendor(request)


def register_vendor(request):
    """تسجيل صاحب محل جديد"""
    if request.user.is_authenticated:
        return redirect('vendor_dashboard')
    
    if request.method == 'POST':
        # بيانات الحساب
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        phone = request.POST.get('phone')
        
        # بيانات المحل
        business_name = request.POST.get('business_name')
        category_id = request.POST.get('category')
        district_id = request.POST.get('district')
        address = request.POST.get('address')
        description = request.POST.get('description')
        whatsapp = request.POST.get('whatsapp', '')
        working_hours = request.POST.get('working_hours', '')
        
        # التحقق من صحة البيانات
        if password1 != password2:
            messages.error(request, 'كلمة المرور غير متطابقة!')
            return redirect('register')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'اسم المستخدم موجود بالفعل!')
            return redirect('register')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'البريد الإلكتروني مسجل بالفعل!')
            return redirect('register')
        
        try:
            # إنشاء المستخدم
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password1
            )
            
            # إضافة الهاتف إذا كان الموديل يدعمه
            if hasattr(user, 'phone'):
                user.phone = phone
            if hasattr(user, 'user_type'):
                user.user_type = 'vendor'
            user.save()
            
            # إنشاء المحل
            category = Category.objects.get(id=category_id)
            district = District.objects.get(id=district_id)
            
            business = Business.objects.create(
                owner=user,
                name=business_name,
                category=category,
                district=district,
                phone=phone,
                whatsapp=whatsapp,
                address=address,
                description=description,
                working_hours=working_hours,
                is_active=False,  # سيتم التفعيل بعد المراجعة
                is_verified=False
            )
            
            # إنشاء اشتراك مجاني تلقائي
            try:
                free_plan = SubscriptionPlan.objects.get(name='free')
                Subscription.objects.create(
                    business=business,
                    plan=free_plan,
                    start_date=timezone.now(),
                    end_date=timezone.now() + timedelta(days=365),
                    status='active'
                )
            except SubscriptionPlan.DoesNotExist:
                pass
            
            # تسجيل الدخول تلقائياً
            login(request, user)
            
            messages.success(
                request, 
                '✅ تم إنشاء حسابك بنجاح! سيتم مراجعة محلك والتفعيل خلال 24 ساعة.'
            )
            return redirect('vendor_dashboard')
            
        except Exception as e:
            messages.error(request, f'❌ حدث خطأ: {str(e)}')
            return redirect('register')
    
    # GET request
    categories = Category.objects.filter(is_active=True).order_by('order')
    districts = District.objects.filter(is_active=True).order_by('name')
    
    context = {
        'categories': categories,
        'districts': districts,
    }
    
    return render(request, 'accounts/register.html', context)


def user_logout(request):
    """تسجيل الخروج"""
    logout(request)
    messages.success(request, 'تم تسجيل الخروج بنجاح! 👋')
    return redirect('home')


# ============================================
# ADMIN DASHBOARD - لوحة تحكم المسؤولين
# ============================================

@login_required
@user_passes_test(lambda u: u.is_staff or u.is_superuser)
def admin_dashboard(request):
    """
    لوحة تحكم الإدارة
    """
    
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
    total_reviews = 0
    approved_reviews = 0
    pending_reviews = 0
    latest_reviews = []
    
    try:
        from reviews.models import Review
        total_reviews = Review.objects.count()
        approved_reviews = Review.objects.filter(is_approved=True).count()
        pending_reviews = Review.objects.filter(is_approved=False).count()
        
        # أحدث التقييمات (آخر 5)
        latest_reviews = Review.objects.select_related(
            'business', 'user'
        ).order_by('-created_at')[:5]
        
    except Exception as e:
        print(f"خطأ في جلب التقييمات: {e}")
    
    # أحدث المحلات
    latest_businesses = Business.objects.select_related(
        'category', 'district', 'owner'
    ).order_by('-created_at')[:5]
    
    # المحلات المعلقة
    pending_businesses_list = Business.objects.filter(
        is_verified=False
    ).select_related('category', 'district', 'owner').order_by('-created_at')[:5]
    
    # ✅ أكثر الفئات استخداماً
    top_categories = Category.objects.annotate(
        business_count=Count('business')  # ← related_query_name (مفرد)
    ).order_by('-business_count')[:5]
    
    # ✅ أكثر المحافظات نشاطاً
    top_governorates = Governorate.objects.annotate(
        business_count=Count('district__business', distinct=True)  # ← district (مفرد) ← business (مفرد)
    ).order_by('-business_count')[:5]
    
    # إحصائيات للـ stats object (للـ Sidebar)
    stats = {
        'total_businesses': total_businesses,
        'active_businesses': active_businesses,
        'pending_businesses': pending_businesses,
        'total_reviews': total_reviews,
        'pending_reviews': pending_reviews,
    }
    
    context = {
        # إحصائيات عامة
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
        
        # قوائم
        'latest_businesses': latest_businesses,
        'pending_businesses_list': pending_businesses_list,
        'latest_reviews': latest_reviews,
        'top_categories': top_categories,
        'top_governorates': top_governorates,
        
        # للـ Sidebar
        'stats': stats,
        'page_title': 'لوحة التحكم',
    }
    
    return render(request, 'accounts/dashboard.html', context)

# ============================================
# MANAGE BUSINESSES - إدارة المحلات (للمسؤولين)
# ============================================

@login_required
@user_passes_test(lambda u: u.is_staff or u.is_superuser)
def manage_businesses(request):
    """
    إدارة المحلات - للإدارة فقط
    """
    from django.db.models import Q, Count
    from django.core.paginator import Paginator
    
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
        businesses = businesses.filter(is_verified=False)  # ← صح - على Business
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
    paginator = Paginator(businesses, 20)  # 20 محل في الصفحة
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
def add_business_admin(request):
    """إضافة محل جديد"""
    
    if request.method == 'POST':
        form = BusinessForm(request.POST, request.FILES)
        
        if form.is_valid():
            business = form.save(commit=False)
            business.owner = request.user
            business.save()
            
            messages.success(request, '✅ تم إضافة المحل بنجاح! بانتظار المراجعة.')
            return redirect('vendor_dashboard')
    else:
        form = BusinessForm()
    
    context = {
        'form': form,
        'page_title': 'إضافة محل جديد'
    }
    
    return render(request, 'accounts/add_business_admin.html', context)


@login_required
def edit_business_admin(request, pk):
    """تعديل محل"""
    
    business = get_object_or_404(Business, pk=pk, owner=request.user)
    
    if request.method == 'POST':
        form = BusinessForm(request.POST, request.FILES, instance=business)
        
        if form.is_valid():
            form.save()
            messages.success(request, '✅ تم تحديث المحل بنجاح!')
            return redirect('vendor_dashboard')
    else:
        form = BusinessForm(instance=business)
    
    context = {
        'form': form,
        'business': business,
        'page_title': 'تعديل المحل'
    }
    
    return render(request, 'accounts/edit_business_admin.html', context)

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
# MANAGE CATEGORIES - إدارة الفئات (للمسؤولين)
# ============================================

@login_required
@user_passes_test(is_staff_or_superuser)
def manage_categories(request):
    """إدارة الفئات"""
    
    # جلب جميع الفئات مع عدد المحلات
    categories = Category.objects.annotate(
        business_count=Count('business')  # ✅ مفرد
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
        'stats': get_admin_stats(),  # ← أضف هنا
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
# MANAGE REVIEWS - إدارة التقييمات (للمسؤولين)
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
        reviews = reviews.filter(is_approved=False)  # ← صحّح لـ is_approved
    elif status == 'verified':
        reviews = reviews.filter(is_approved=True)  # ← صحّح لـ is_approved
    
    # Pagination - 10 تقييمات في الصفحة
    paginator = Paginator(reviews, 10)
    page_number = request.GET.get('page')
    
    try:
        reviews_page = paginator.get_page(page_number)
    except PageNotAnInteger:
        reviews_page = paginator.get_page(1)
    except EmptyPage:
        reviews_page = paginator.get_page(paginator.num_pages)
    
    context = {
        'reviews': reviews_page,
        'total_count': paginator.count,
        'pending_count': Review.objects.filter(is_approved=False).count(),  # ← صحّح
        'current_status': status,
    }
    
    return render(request, 'accounts/manage_reviews.html', context)


@login_required
@user_passes_test(is_staff_or_superuser)
def approve_review(request, pk):
    """الموافقة على تقييم"""
    review = get_object_or_404(Review, pk=pk)
    
    if request.method == 'POST' or request.method == 'GET':  # ← اسمح بـ GET
        review.is_approved = True  # ← صحّح لـ is_approved
        review.save()
        messages.success(request, f'✅ تمت الموافقة على تقييم {review.reviewer_name}')
    
    return redirect('manage_reviews')


@login_required
@user_passes_test(is_staff_or_superuser)
def delete_review(request, pk):
    """حذف تقييم"""
    review = get_object_or_404(Review, pk=pk)
    
    if request.method == 'POST' or request.method == 'GET':  # ← اسمح بـ GET
        review_name = review.reviewer_name
        business_name = review.business.name
        review.delete()
        messages.success(request, f'✅ تم حذف تقييم {review_name} على {business_name}')
    
    return redirect('manage_reviews')


@login_required
@user_passes_test(is_staff_or_superuser)
def delete_review(request, pk):
    """حذف تقييم"""
    review = get_object_or_404(Review, pk=pk)
    
    if request.method == 'POST':
        review.delete()
        messages.success(request, 'تم حذف التقييم بنجاح!')
        return redirect('manage_reviews')
    
    context = {'review': review}
    return render(request, 'accounts/delete_review_confirm.html', context)


# ============================================
# VENDOR DASHBOARD - لوحة تحكم أصحاب المحلات
# ============================================

@login_required
def vendor_dashboard(request):
    """لوحة تحكم صاحب المحل"""
    
    # إذا كان مسؤول، يتم توجيهه للوحة المسؤولين
    if request.user.is_staff or request.user.is_superuser:
        return redirect('admin_dashboard')
    
    # التحقق من نوع المستخدم
    if hasattr(request.user, 'user_type') and request.user.user_type != 'vendor':
        messages.error(request, 'غير مصرح لك بالوصول لهذه الصفحة')
        return redirect('home')
    
    # محلات المستخدم
    businesses = Business.objects.filter(
        owner=request.user
    ).select_related('category', 'district')
    
    # إحصائيات
    total_views = sum([b.view_count for b in businesses])
    total_products = Product.objects.filter(business__owner=request.user).count()
    total_reviews = sum([getattr(b, 'total_reviews', 0) for b in businesses])
    
    # آخر المنتجات
    latest_products = Product.objects.filter(
        business__owner=request.user
    ).select_related('business').order_by('-created_at')[:5]
    
    context = {
        'businesses': businesses,
        'total_businesses': businesses.count(),
        'active_businesses': businesses.filter(is_active=True).count(),
        'total_views': total_views,
        'total_products': total_products,
        'total_reviews': total_reviews,
        'latest_products': latest_products,
    }
    
    return render(request, 'accounts/vendor_dashboard.html', context)


# ============================================
# BUSINESS MANAGEMENT - إدارة المحل (للبائعين)
# ============================================

@login_required
def edit_business(request, pk):
    """تعديل بيانات المحل"""
    business = get_object_or_404(Business, pk=pk, owner=request.user)
    
    if request.method == 'POST':
        # البيانات الأساسية
        business.name = request.POST.get('name')
        business.category_id = request.POST.get('category')
        business.district_id = request.POST.get('district')
        business.description = request.POST.get('description')
        
        # معلومات الاتصال
        business.phone = request.POST.get('phone')
        business.whatsapp = request.POST.get('whatsapp', '')
        business.email = request.POST.get('email', '')
        business.working_hours = request.POST.get('working_hours', '')
        
        # الموقع
        business.address = request.POST.get('address')
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        
        if latitude:
            business.latitude = latitude
        if longitude:
            business.longitude = longitude
        
        # اللوجو
        if request.FILES.get('logo'):
            business.logo = request.FILES['logo']
        
        business.save()
        
        messages.success(request, 'تم تحديث بيانات المحل بنجاح! ✅')
        return redirect('vendor_dashboard')
    
    # GET request
    categories = Category.objects.filter(is_active=True).order_by('order')
    districts = District.objects.filter(is_active=True).order_by('name')
    
    context = {
        'business': business,
        'categories': categories,
        'districts': districts,
    }
    
    return render(request, 'accounts/edit_business.html', context)


# ============================================
# PRODUCTS MANAGEMENT - إدارة المنتجات (للبائعين)
# ============================================

@login_required
def manage_products(request):
    """إدارة المنتجات"""
    products = Product.objects.filter(
        business__owner=request.user
    ).select_related('business').order_by('-created_at')
    
    context = {
        'products': products,
        'total_count': products.count(),
    }
    
    return render(request, 'accounts/manage_products.html', context)


@login_required
def add_product(request):
    """إضافة منتج جديد"""
    businesses = Business.objects.filter(owner=request.user)
    
    if not businesses.exists():
        messages.error(request, 'يجب أن يكون لديك محل مسجّل أولاً.')
        return redirect('vendor_dashboard')
    
    if request.method == 'POST':
        business_id = request.POST.get('business')
        name = request.POST.get('name')
        description = request.POST.get('description')
        price = request.POST.get('price')
        delivery_cost = request.POST.get('delivery_cost') or 0
        is_available = request.POST.get('is_available') == 'on'
        has_delivery = request.POST.get('has_delivery') == 'on'
        order = request.POST.get('order') or 0
        
        # التحقق من ملكية المحل
        business = get_object_or_404(Business, id=business_id, owner=request.user)
        
        # إنشاء المنتج
        Product.objects.create(
            business=business,
            name=name,
            description=description,
            price=price,
            delivery_cost=delivery_cost,
            is_available=is_available,
            has_delivery=has_delivery,
            order=order
        )
        
        messages.success(request, f'✅ تم إضافة "{name}" بنجاح!')
        return redirect('manage_products')
    
    context = {
        'businesses': businesses,
    }
    return render(request, 'accounts/add_product.html', context)


@login_required
def edit_product(request, pk):
    """تعديل منتج"""
    product = get_object_or_404(
        Product,
        pk=pk,
        business__owner=request.user
    )
    
    businesses = Business.objects.filter(owner=request.user)
    
    if request.method == 'POST':
        product.business_id = request.POST.get('business')
        product.name = request.POST.get('name')
        product.description = request.POST.get('description')
        product.price = request.POST.get('price')
        product.delivery_cost = request.POST.get('delivery_cost') or 0
        product.is_available = request.POST.get('is_available') == 'on'
        product.has_delivery = request.POST.get('has_delivery') == 'on'
        product.order = request.POST.get('order') or 0
        
        product.save()
        
        messages.success(request, f'✅ تم تحديث "{product.name}" بنجاح!')
        return redirect('manage_products')
    
    context = {
        'product': product,
        'businesses': businesses,
    }
    return render(request, 'accounts/edit_product.html', context)


@login_required
def delete_product(request, pk):
    """حذف منتج"""
    product = get_object_or_404(
        Product,
        pk=pk,
        business__owner=request.user
    )
    
    if request.method == 'POST':
        product_name = product.name
        product.delete()
        messages.success(request, f'تم حذف "{product_name}" بنجاح!')
        return redirect('manage_products')
    
    return render(request, 'accounts/delete_product.html', {'product': product})


@login_required
def import_products(request):
    """استيراد منتجات من ملف CSV"""
    businesses = Business.objects.filter(owner=request.user)
    
    if not businesses.exists():
        messages.error(request, 'يجب أن يكون لديك محل مسجّل أولاً.')
        return redirect('vendor_dashboard')
    
    if request.method == 'POST':
        business_id = request.POST.get('business')
        file = request.FILES.get('file')
        
        if not business_id or not file:
            messages.error(request, 'من فضلك اختر المحل والملف أولاً.')
            return redirect('import_products')
        
        business = get_object_or_404(Business, id=business_id, owner=request.user)
        
        # التحقق من نوع الملف
        if not file.name.lower().endswith('.csv'):
            messages.error(request, 'يجب رفع ملف بصيغة CSV.')
            return redirect('import_products')
        
        try:
            decoded_file = TextIOWrapper(file.file, encoding='utf-8')
            reader = csv.DictReader(decoded_file)
            
            products_to_create = []
            row_number = 1
            
            with transaction.atomic():
                for row in reader:
                    row_number += 1
                    name = row.get('name')
                    description = row.get('description', '')
                    price = row.get('price')
                    is_available = row.get('is_available', '1')
                    has_delivery = row.get('has_delivery', '0')
                    
                    if not name or not price:
                        raise ValueError(f'سطر {row_number}: الاسم أو السعر مفقود.')
                    
                    products_to_create.append(Product(
                        business=business,
                        name=name.strip(),
                        description=description.strip(),
                        price=price,
                        is_available=is_available in ['1', 'True', 'true'],
                        has_delivery=has_delivery in ['1', 'True', 'true'],
                    ))
                
                Product.objects.bulk_create(products_to_create)
            
            messages.success(request, f'✅ تم استيراد {len(products_to_create)} منتج بنجاح!')
            return redirect('manage_products')
        
        except Exception as e:
            messages.error(request, f'❌ حدث خطأ أثناء الاستيراد: {e}')
            return redirect('import_products')
    
    context = {
        'businesses': businesses,
    }
    return render(request, 'accounts/import_products.html', context)


# ============================================
# REPORTS & STATISTICS - التقارير والإحصائيات
# ============================================

@login_required
def reports(request):
    """التقارير والإحصائيات للبائع"""
    if hasattr(request.user, 'user_type') and request.user.user_type != 'vendor':
        messages.error(request, 'غير مصرح لك بالوصول لهذه الصفحة')
        return redirect('home')
    
    businesses = Business.objects.filter(owner=request.user).select_related('category')
    
    total_views = sum([b.view_count for b in businesses])
    total_products = Product.objects.filter(business__owner=request.user).count()
    total_reviews = sum([getattr(b, 'total_reviews', 0) for b in businesses])
    
    # أفضل المنتجات
    top_products = Product.objects.filter(
        business__owner=request.user
    ).select_related('business').order_by('-created_at')[:10]
    
    context = {
        'businesses': businesses,
        'total_businesses': businesses.count(),
        'total_views': total_views,
        'total_products': total_products,
        'total_reviews': total_reviews,
        'top_products': top_products,
    }
    
    return render(request, 'accounts/reports.html', context)


# ============================================
# SUBSCRIPTION - الاشتراكات
# ============================================

@login_required
def upgrade_subscription_page(request):
    """صفحة عرض خطط الاشتراك"""
    plans = SubscriptionPlan.objects.all().order_by('price_yearly')
    
    # الخطة الحالية
    current_plan = None
    user_business = Business.objects.filter(owner=request.user).first()
    if user_business:
        try:
            subscription = Subscription.objects.get(business=user_business, status='active')
            current_plan = subscription.plan.name
        except Subscription.DoesNotExist:
            pass
    
    context = {
        'plans': plans,
        'current_plan': current_plan,
    }
    
    return render(request, 'accounts/upgrade_subscription.html', context)


@login_required
def upgrade_subscription(request, plan_id):
    """تنفيذ ترقية الاشتراك"""
    plan = get_object_or_404(SubscriptionPlan, id=plan_id)
    
    # TODO: إضافة منطق الدفع لاحقاً
    messages.info(
        request, 
        f'جاري العمل على تفعيل خطة "{plan.display_name}". سيتم التواصل معك قريباً! 📞'
    )
    
    return redirect('vendor_dashboard')


# ============================================
# SETTINGS - الإعدادات
# ============================================


@login_required
def settings(request):
    """إعدادات الحساب - معلومات شخصية وكلمة المرور فقط"""
    
    user = request.user
    is_admin = user.is_staff or user.is_superuser
    
    # معالجة POST
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
                        # إعادة تسجيل الدخول تلقائياً
                        from django.contrib.auth import update_session_auth_hash
                        update_session_auth_hash(request, user)
                    except Exception as e:
                        messages.error(request, f'❌ حدث خطأ: {str(e)}')
                else:
                    messages.error(request, '❌ كلمة المرور غير متطابقة!')
            else:
                messages.warning(request, '⚠️ الرجاء إدخال كلمة المرور في الحقلين!')
        
        return redirect('dashboard_settings')
    
    # Vendors للمسؤولين فقط
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


# ============================================
# MANAGE VENDORS - إدارة أصحاب المحلات
# ============================================

@login_required
@user_passes_test(is_staff_or_superuser)
def add_vendor(request):
    """إضافة صاحب محل جديد"""
    
    if request.method == 'POST':
        # بيانات الحساب
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        phone = request.POST.get('phone', '')
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        
        # التحقق من البيانات
        if User.objects.filter(username=username).exists():
            messages.error(request, '❌ اسم المستخدم موجود بالفعل!')
            return redirect('add_vendor')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, '❌ البريد الإلكتروني مسجل بالفعل!')
            return redirect('add_vendor')
        
        try:
            # إنشاء المستخدم
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )
            
            # إضافة البيانات الإضافية
            if hasattr(user, 'phone'):
                user.phone = phone
            if hasattr(user, 'user_type'):
                user.user_type = 'vendor'
            user.save()
            
            messages.success(request, f'✅ تم إضافة صاحب المحل "{username}" بنجاح!')
            return redirect('dashboard_settings')
            
        except Exception as e:
            messages.error(request, f'❌ حدث خطأ: {str(e)}')
            return redirect('add_vendor')
    
    return render(request, 'accounts/add_vendor.html')


@login_required
@user_passes_test(is_staff_or_superuser)
def edit_vendor(request, pk):
    """تعديل بيانات صاحب محل"""
    
    vendor = get_object_or_404(User, pk=pk)
    
    if request.method == 'POST':
        vendor.email = request.POST.get('email')
        vendor.first_name = request.POST.get('first_name', '')
        vendor.last_name = request.POST.get('last_name', '')
        
        if hasattr(vendor, 'phone'):
            vendor.phone = request.POST.get('phone', '')
        
        # تحديث كلمة المرور (اختياري)
        new_password = request.POST.get('new_password')
        if new_password:
            vendor.set_password(new_password)
        
        # تحديث الحالة
        vendor.is_active = request.POST.get('is_active') == 'on'
        
        vendor.save()
        messages.success(request, f'✅ تم تحديث بيانات "{vendor.username}" بنجاح!')
        return redirect('dashboard_settings')
    
    context = {
        'vendor': vendor,
    }
    
    return render(request, 'accounts/edit_vendor.html', context)


@login_required
@user_passes_test(is_staff_or_superuser)
def delete_vendor(request, pk):
    """حذف صاحب محل"""
    
    vendor = get_object_or_404(User, pk=pk)
    
    # التحقق من عدم وجود محلات
    if vendor.businesses.exists():
        messages.error(
            request, 
            f'❌ لا يمكن حذف "{vendor.username}" لأنه يمتلك {vendor.businesses.count()} محل!'
        )
        return redirect('dashboard_settings')
    
    if request.method == 'POST':
        username = vendor.username
        vendor.delete()
        messages.success(request, f'✅ تم حذف "{username}" بنجاح!')
        return redirect('dashboard_settings')
    
    context = {
        'vendor': vendor,
    }
    
    return render(request, 'accounts/delete_vendor_confirm.html', context)


@login_required
@user_passes_test(is_staff_or_superuser)
def toggle_vendor_status(request, pk):
    """تفعيل/إيقاف حساب صاحب محل"""
    
    vendor = get_object_or_404(User, pk=pk)
    vendor.is_active = not vendor.is_active
    vendor.save()
    
    status = "تم تفعيل" if vendor.is_active else "تم إيقاف"
    messages.success(request, f'{status} حساب "{vendor.username}" بنجاح!')
    
    return redirect('dashboard_settings')

@login_required
@user_passes_test(is_staff_or_superuser)
def manage_governorates(request):
    """إدارة المحافظات"""
    
    # ============================================
    # 🔄 تبديل حالة التفعيل (هنا الأول!)
    # ============================================
    if request.method == 'POST':
        print(f"📩 POST Data: {request.POST}")  # ← Debug
        
        if 'toggle_active' in request.POST:
            print("✅ toggle_active detected!")  # ← Debug
            
            governorate_id = request.POST.get('governorate_id')
            print(f"🆔 Governorate ID: {governorate_id}")  # ← Debug
            
            if not governorate_id:
                messages.error(request, 'معرف المحافظة مفقود!')
                return redirect('manage_governorates')
            
            try:
                governorate = get_object_or_404(Governorate, id=governorate_id)
                print(f"🏛️ Before: {governorate.name} - is_active={governorate.is_active}")  # ← Debug
                
                # تبديل الحالة
                governorate.is_active = not governorate.is_active
                governorate.save()
                
                print(f"🏛️ After: {governorate.name} - is_active={governorate.is_active}")  # ← Debug
                
                status = 'تم تفعيل' if governorate.is_active else 'تم إلغاء تفعيل'
                messages.success(request, f'{status} المحافظة "{governorate.name}" بنجاح!')
                
            except Exception as e:
                print(f"❌ Error: {str(e)}")  # ← Debug
                messages.error(request, f'حدث خطأ: {str(e)}')
            
            return redirect('manage_governorates')
    
    # ============================================
    # ➕ إضافة محافظة جديدة
    # ============================================
    if request.method == 'POST' and 'add_governorate' in request.POST:
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
                is_active=True,
            )
            messages.success(request, f'تم إضافة المحافظة "{name}" بنجاح!')
            return redirect('manage_governorates')
        else:
            messages.error(request, 'يرجى إدخال اسم المحافظة.')
    
    # ============================================
    # ✏️ تعديل محافظة
    # ============================================
    if request.method == 'POST' and 'edit_governorate' in request.POST:
        governorate_id = request.POST.get('governorate_id')
        
        if not governorate_id:
            messages.error(request, 'معرف المحافظة مفقود!')
            return redirect('manage_governorates')
        
        try:
            governorate = get_object_or_404(Governorate, id=governorate_id)
            
            governorate.name = request.POST.get('name')
            governorate.name_en = request.POST.get('name_en', '')
            governorate.description = request.POST.get('description', '')
            governorate.icon = request.POST.get('icon', 'fas fa-city')
            governorate.order = request.POST.get('order', 0)
            governorate.is_active = request.POST.get('is_active') == 'on'
            
            # معالجة الصورة
            if 'image' in request.FILES:
                governorate.image = request.FILES['image']
            
            governorate.save()
            
            messages.success(request, f'تم تحديث المحافظة "{governorate.name}" بنجاح!')
        except Exception as e:
            messages.error(request, f'حدث خطأ: {str(e)}')
        
        return redirect('manage_governorates')
    
    # ============================================
    # 🗑️ حذف محافظة
    # ============================================
    if request.method == 'POST' and 'delete_governorate' in request.POST:
        governorate_id = request.POST.get('governorate_id')
        
        if not governorate_id:
            messages.error(request, 'معرف المحافظة مفقود!')
            return redirect('manage_governorates')
        
        try:
            governorate = get_object_or_404(Governorate, id=governorate_id)
            
            # التحقق من عدم وجود محلات مرتبطة
            business_count = Business.objects.filter(district__governorate=governorate).count()
            
            if business_count > 0:
                messages.error(
                    request, 
                    f'لا يمكن حذف المحافظة "{governorate.name}" لأنها تحتوي على {business_count} محل.'
                )
            else:
                governorate_name = governorate.name
                governorate.delete()
                messages.success(request, f'تم حذف المحافظة "{governorate_name}" بنجاح!')
        except Exception as e:
            messages.error(request, f'حدث خطأ: {str(e)}')
        
        return redirect('manage_governorates')
    
    # ============================================
    # 📊 جلب البيانات والإحصائيات
    # ============================================
    governorates = Governorate.objects.annotate(
        district_count=Count('district', distinct=True),
        business_count=Count('district__business', distinct=True),
        active_business_count=Count(
            'district__business',
            filter=Q(district__business__is_active=True),
            distinct=True
        )
    ).order_by('order', 'name')
    
    # إحصائيات عامة
    total_governorates = governorates.count()
    active_governorates = governorates.filter(is_active=True).count()
    total_businesses = Business.objects.count()
    total_districts = District.objects.count()
    
    context = {
        'governorates': governorates,
        'total_governorates': total_governorates,
        'active_governorates': active_governorates,
        'total_businesses': total_businesses,
        'total_districts': total_districts,
        'stats': get_admin_stats(),
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


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Q, Count
from django.core.paginator import Paginator
from accounts.models import User
from directory.models import Business


# ============================================
# إدارة المستخدمين
# ============================================

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Q, Count
from django.core.paginator import Paginator
from accounts.models import User
from directory.models import Business  # ← تأكد من الـ import

@login_required
@user_passes_test(lambda u: u.is_staff or u.is_superuser)
def manage_users(request):
    """قائمة المستخدمين"""
    search_query = request.GET.get('search', '')
    user_type = request.GET.get('type', '')
    status = request.GET.get('status', '')
    
    users = User.objects.annotate(
        businesses_count=Count('business')
    ).order_by('-date_joined')
    
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query)
        )
    
    if user_type:
        users = users.filter(user_type=user_type)
    
    if status == 'active':
        users = users.filter(is_active=True)
    elif status == 'inactive':
        users = users.filter(is_active=False)
    
    paginator = Paginator(users, 20)
    page_number = request.GET.get('page')
    users_page = paginator.get_page(page_number)
    
    context = {
        'users': users_page,
        'search_query': search_query,
        'user_type': user_type,
        'status': status,
        'total_users': User.objects.count(),
        'active_users': User.objects.filter(is_active=True).count(),
        'vendors': User.objects.filter(user_type='vendor').count(),
    }
    
    return render(request, 'accounts/admin/manage_users.html', context)


@login_required
@user_passes_test(lambda u: u.is_staff or u.is_superuser)
def edit_user(request, pk):
    """تعديل بيانات المستخدم"""
    user_obj = get_object_or_404(User, pk=pk)
    
    if request.method == 'POST':
        user_obj.first_name = request.POST.get('first_name', '')
        user_obj.last_name = request.POST.get('last_name', '')
        user_obj.email = request.POST.get('email', '')
        user_obj.phone = request.POST.get('phone', '')
        user_obj.user_type = request.POST.get('user_type', 'customer')
        user_obj.is_active = request.POST.get('is_active') == 'on'
        user_obj.is_verified = request.POST.get('is_verified') == 'on'
        user_obj.is_staff = request.POST.get('is_staff') == 'on'
        
        user_obj.save()
        
        messages.success(request, f'✅ تم تحديث بيانات {user_obj.get_full_name() or user_obj.username} بنجاح!')
        return redirect('manage_users')
    
    context = {
        'user_obj': user_obj,
    }
    
    return render(request, 'accounts/admin/edit_user.html', context)


@login_required
@user_passes_test(lambda u: u.is_staff or u.is_superuser)
def delete_user(request, pk):
    """حذف المستخدم"""
    from directory.models import Business
    
    user_obj = get_object_or_404(User, pk=pk)
    
    if user_obj == request.user:
        messages.error(request, '❌ لا يمكنك حذف حسابك الخاص!')
        return redirect('manage_users')
    
    if user_obj.is_superuser:
        messages.error(request, '❌ لا يمكن حذف المدير الرئيسي!')
        return redirect('manage_users')
    
    if request.method == 'POST':
        username = user_obj.get_full_name() or user_obj.username
        user_obj.delete()
        messages.success(request, f'✅ تم حذف المستخدم {username} بنجاح!')
        return redirect('manage_users')
    
    # حساب الإحصائيات
    businesses = Business.objects.filter(owner=user_obj)
    businesses_count = businesses.count()
    products_count = sum([b.products.count() for b in businesses])
    
    context = {
        'user_obj': user_obj,
        'businesses_count': businesses_count,
        'products_count': products_count,
    }
    
    return render(request, 'accounts/admin/delete_user.html', context)


@login_required
@user_passes_test(lambda u: u.is_staff or u.is_superuser)
def toggle_user_status(request, pk):
    """تفعيل/تعطيل المستخدم"""
    user_obj = get_object_or_404(User, pk=pk)
    
    if user_obj == request.user:
        messages.error(request, '❌ لا يمكنك تعطيل حسابك الخاص!')
        return redirect('manage_users')
    
    user_obj.is_active = not user_obj.is_active
    user_obj.save()
    
    status = 'تفعيل' if user_obj.is_active else 'تعطيل'
    messages.success(request, f'✅ تم {status} حساب {user_obj.get_full_name() or user_obj.username}')
    
    return redirect('manage_users')


@login_required
@user_passes_test(lambda u: u.is_staff or u.is_superuser)
def user_businesses(request, user_id):
    """عرض محلات المستخدم"""
    from directory.models import Business
    
    user_obj = get_object_or_404(User, pk=user_id)
    
    # ✅ جلب المحلات مع الـ relationships الصحيحة
    businesses = Business.objects.filter(owner=user_obj).select_related(
        'category',
        'district',
        'district__governorate'  # ✅ الوصول للمحافظة من خلال الحي
    ).prefetch_related('images').order_by('-created_at')
    
    context = {
        'user_obj': user_obj,
        'businesses': businesses,
    }
    
    return render(request, 'accounts/admin/user_businesses.html', context)


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Q, Count
from django.core.paginator import Paginator
from accounts.models import User
from directory.models import Business, Category, District, Governorate


# ... الـ views القديمة ...


@login_required
@user_passes_test(lambda u: u.is_staff or u.is_superuser)
def edit_business_admin(request, pk):
    """تعديل محل تجاري"""
    from directory.models import Business, Category, District, Governorate
    
    business = get_object_or_404(Business, pk=pk)
    
    if request.method == 'POST':
        # تحديث البيانات الأساسية
        business.name = request.POST.get('name', '')
        business.phone = request.POST.get('phone', '')
        business.whatsapp = request.POST.get('whatsapp', '')
        business.email = request.POST.get('email', '')
        business.address = request.POST.get('address', '')
        business.description = request.POST.get('description', '')
        business.working_hours = request.POST.get('working_hours', '')
        
        # تحديث الفئة والموقع
        category_id = request.POST.get('category')
        district_id = request.POST.get('district')
        
        if category_id:
            business.category_id = category_id
        if district_id:
            business.district_id = district_id
        
        # تحديث الحالات
        business.is_active = request.POST.get('is_active') == 'on'
        business.is_verified = request.POST.get('is_verified') == 'on'
        business.is_featured = request.POST.get('is_featured') == 'on'
        
        # تحديث اللوجو
        if 'logo' in request.FILES:
            business.logo = request.FILES['logo']
        
        business.save()
        
        messages.success(request, f'✅ تم تحديث محل {business.name} بنجاح!')
        return redirect('user_businesses', business.owner.id)
    
    # جلب البيانات
    categories = Category.objects.filter(is_active=True).order_by('name')
    governorates = Governorate.objects.filter(is_active=True).order_by('name')
    districts = District.objects.filter(is_active=True).order_by('governorate__name', 'name')
    
    context = {
        'business': business,
        'categories': categories,
        'governorates': governorates,
        'districts': districts,
    }
    
    return render(request, 'accounts/admin/edit_business.html', context)


@login_required
@user_passes_test(lambda u: u.is_staff or u.is_superuser)
def toggle_business_status(request, pk):
    """تفعيل/تعطيل محل"""
    from directory.models import Business
    
    business = get_object_or_404(Business, pk=pk)
    business.is_active = not business.is_active
    business.save()
    
    status = 'تفعيل' if business.is_active else 'تعطيل'
    messages.success(request, f'✅ تم {status} محل {business.name}')
    
    return redirect('user_businesses', business.owner.id)


@login_required
@user_passes_test(lambda u: u.is_staff or u.is_superuser)
def add_business_admin(request):
    """إضافة محل جديد"""
    from directory.models import Business, Category, District, Governorate
    
    if request.method == 'POST':
        # إنشاء المحل
        owner_id = request.POST.get('owner')
        owner = get_object_or_404(User, pk=owner_id)
        
        business = Business.objects.create(
            owner=owner,
            name=request.POST.get('name', ''),
            phone=request.POST.get('phone', ''),
            whatsapp=request.POST.get('whatsapp', ''),
            email=request.POST.get('email', ''),
            address=request.POST.get('address', ''),
            description=request.POST.get('description', ''),
            working_hours=request.POST.get('working_hours', ''),
            category_id=request.POST.get('category'),
            district_id=request.POST.get('district'),
            is_active=request.POST.get('is_active') == 'on',
            is_verified=request.POST.get('is_verified') == 'on',
            is_featured=request.POST.get('is_featured') == 'on',
        )
        
        # رفع اللوجو
        if 'logo' in request.FILES:
            business.logo = request.FILES['logo']
            business.save()
        
        messages.success(request, f'✅ تم إضافة محل {business.name} بنجاح!')
        return redirect('manage_businesses')
    
    # جلب البيانات
    categories = Category.objects.filter(is_active=True).order_by('name')
    governorates = Governorate.objects.filter(is_active=True).order_by('name')
    districts = District.objects.filter(is_active=True).order_by('governorate__name', 'name')
    users = User.objects.filter(user_type='vendor', is_active=True).order_by('username')
    
    context = {
        'categories': categories,
        'governorates': governorates,
        'districts': districts,
        'users': users,
    }
    
    return render(request, 'accounts/admin/add_business.html', context)

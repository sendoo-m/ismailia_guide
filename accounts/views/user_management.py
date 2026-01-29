"""
User Management Views
=====================
إدارة المستخدمين والمحلات (للإدارة فقط)
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.contrib.auth import get_user_model

from directory.models import Business, Category, District, Governorate

User = get_user_model()


# ============================================
# إدارة المستخدمين
# ============================================

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
    user_obj = get_object_or_404(User, pk=user_id)
    
    businesses = Business.objects.filter(owner=user_obj).select_related(
        'category',
        'district',
        'district__governorate'
    ).prefetch_related('images').order_by('-created_at')
    
    context = {
        'user_obj': user_obj,
        'businesses': businesses,
    }
    
    return render(request, 'accounts/admin/user_businesses.html', context)


# ============================================
# إدارة المحلات (للإدارة)
# ============================================

@login_required
@user_passes_test(lambda u: u.is_staff or u.is_superuser)
def edit_business_admin(request, pk):
    """تعديل محل تجاري"""
    business = get_object_or_404(Business, pk=pk)
    
    if request.method == 'POST':
        business.name = request.POST.get('name', '')
        business.phone = request.POST.get('phone', '')
        business.whatsapp = request.POST.get('whatsapp', '')
        business.email = request.POST.get('email', '')
        business.address = request.POST.get('address', '')
        business.description = request.POST.get('description', '')
        business.working_hours = request.POST.get('working_hours', '')
        
        category_id = request.POST.get('category')
        district_id = request.POST.get('district')
        
        if category_id:
            business.category_id = category_id
        if district_id:
            business.district_id = district_id
        
        business.is_active = request.POST.get('is_active') == 'on'
        business.is_verified = request.POST.get('is_verified') == 'on'
        business.is_featured = request.POST.get('is_featured') == 'on'
        
        if 'logo' in request.FILES:
            business.logo = request.FILES['logo']
        
        business.save()
        
        messages.success(request, f'✅ تم تحديث محل {business.name} بنجاح!')
        return redirect('user_businesses', business.owner.id)
    
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
    if request.method == 'POST':
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
        
        if 'logo' in request.FILES:
            business.logo = request.FILES['logo']
            business.save()
        
        messages.success(request, f'✅ تم إضافة محل {business.name} بنجاح!')
        return redirect('manage_businesses')
    
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

"""
Vendor Views
============
لوحة تحكم أصحاب المحلات وإدارة المنتجات
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from io import TextIOWrapper
import csv

from directory.models import Business, Category, District
from products.models import Product
from subscriptions.models import SubscriptionPlan, Subscription


# ============================================
# Vendor Dashboard
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
# Business Management
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
# Products Management
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
# Reports & Subscriptions
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

@login_required
def delete_business(request, pk):
    """حذف محل"""
    business = get_object_or_404(Business, pk=pk, owner=request.user)
    
    if request.method == 'POST':
        business_name = business.name
        
        # حذف جميع المنتجات المرتبطة
        Product.objects.filter(business=business).delete()
        
        # حذف المحل
        business.delete()
        
        messages.success(request, f'✅ تم حذف "{business_name}" وجميع منتجاته بنجاح!')
        return redirect('vendor_dashboard')
    
    # GET request - صفحة التأكيد
    context = {
        'business': business,
        'product_count': Product.objects.filter(business=business).count(),
    }
    return render(request, 'accounts/delete_business.html', context)


@login_required
def dashboard_settings(request):
    """إعدادات لوحة التحكم"""
    if request.method == 'POST':
        # معالجة تحديث البيانات
        user = request.user
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.email = request.POST.get('email', '')
        
        # تحديث كلمة المرور (اختياري)
        new_password = request.POST.get('new_password')
        if new_password:
            user.set_password(new_password)
        
        user.save()
        messages.success(request, '✅ تم تحديث البيانات بنجاح!')
        return redirect('dashboard_settings')
    
    context = {
        'user': request.user,
    }
    return render(request, 'accounts/settings.html', context)

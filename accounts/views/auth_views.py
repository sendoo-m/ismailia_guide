"""
Authentication Views
====================
تسجيل الدخول، التسجيل، تسجيل الخروج
"""

from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta

from directory.models import Business, Category, District
from subscriptions.models import SubscriptionPlan, Subscription

User = get_user_model()


# ============================================
# تسجيل الدخول
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


# ============================================
# التسجيل
# ============================================

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
                is_active=False,
                is_verified=False
            )
            
            # إنشاء اشتراك مجاني
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


# ============================================
# تسجيل الخروج
# ============================================

def user_logout(request):
    """تسجيل الخروج"""
    logout(request)
    messages.success(request, 'تم تسجيل الخروج بنجاح! 👋')
    return redirect('home')

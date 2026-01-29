from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import SubscriptionPlan, Subscription
from directory.models import Business


def plans_list(request):
    """عرض خطط الاشتراك"""
    plans = SubscriptionPlan.objects.filter(is_active=True).order_by('price')
    
    context = {
        'plans': plans,
    }
    return render(request, 'subscriptions/plans_list.html', context)


@login_required
def subscribe(request, plan_id):
    """الاشتراك في خطة"""
    plan = get_object_or_404(SubscriptionPlan, pk=plan_id, is_active=True)
    
    # التحقق من أن المستخدم لديه محل
    businesses = Business.objects.filter(owner=request.user, is_active=True)
    
    if not businesses.exists():
        messages.error(request, 'يجب أن يكون لديك محل نشط للاشتراك.')
        return redirect('subscriptions:plans_list')
    
    if request.method == 'POST':
        business_id = request.POST.get('business')
        business = get_object_or_404(Business, pk=business_id, owner=request.user)
        
        # إنشاء اشتراك جديد
        subscription = Subscription.objects.create(
            business=business,
            plan=plan,
            start_date=timezone.now(),
            end_date=timezone.now() + timezone.timedelta(days=plan.duration_days),
            status='pending',  # في انتظار الدفع
        )
        
        messages.success(request, 'تم إنشاء الاشتراك! يرجى إكمال عملية الدفع.')
        return redirect('payments:checkout', subscription_id=subscription.id)
    
    context = {
        'plan': plan,
        'businesses': businesses,
    }
    return render(request, 'subscriptions/subscribe.html', context)


@login_required
def my_subscriptions(request):
    """اشتراكاتي"""
    subscriptions = Subscription.objects.filter(
        business__owner=request.user
    ).select_related('business', 'plan').order_by('-created_at')
    
    context = {
        'subscriptions': subscriptions,
    }
    return render(request, 'subscriptions/my_subscriptions.html', context)


@login_required
def cancel_subscription(request, subscription_id):
    """إلغاء اشتراك"""
    subscription = get_object_or_404(
        Subscription,
        pk=subscription_id,
        business__owner=request.user
    )
    
    if request.method == 'POST':
        subscription.status = 'cancelled'
        subscription.save()
        
        messages.success(request, 'تم إلغاء الاشتراك بنجاح!')
        return redirect('subscriptions:my_subscriptions')
    
    context = {
        'subscription': subscription,
    }
    return render(request, 'subscriptions/cancel_subscription_confirm.html', context)

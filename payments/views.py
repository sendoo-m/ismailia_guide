from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Payment
from subscriptions.models import Subscription


@login_required
def checkout(request, subscription_id):
    """بوابة الدفع"""
    subscription = get_object_or_404(
        Subscription,
        pk=subscription_id,
        business__owner=request.user
    )
    
    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')
        
        # إنشاء عملية دفع
        payment = Payment.objects.create(
            subscription=subscription,
            amount=subscription.plan.price,
            payment_method=payment_method,
            status='pending',
        )
        
        messages.success(request, 'تم إرسال طلب الدفع! سيتم مراجعته قريباً.')
        return redirect('payments:payment_confirm', payment_id=payment.id)
    
    context = {
        'subscription': subscription,
    }
    return render(request, 'payments/checkout.html', context)


@login_required
def payment_confirm(request, payment_id):
    """تأكيد الدفع"""
    payment = get_object_or_404(
        Payment,
        pk=payment_id,
        subscription__business__owner=request.user
    )
    
    context = {
        'payment': payment,
    }
    return render(request, 'payments/payment_confirm.html', context)


@login_required
def payment_history(request):
    """سجل المدفوعات"""
    payments = Payment.objects.filter(
        subscription__business__owner=request.user
    ).select_related('subscription', 'subscription__plan', 'subscription__business').order_by('-created_at')
    
    context = {
        'payments': payments,
    }
    return render(request, 'payments/payment_history.html', context)

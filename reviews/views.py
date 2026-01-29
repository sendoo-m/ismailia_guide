from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Review
from directory.models import Business


def add_review(request, business_slug):
    """إضافة تقييم لمحل"""
    business = get_object_or_404(Business, slug=business_slug, is_active=True)
    
    if request.method == 'POST':
        reviewer_name = request.POST.get('reviewer_name')
        reviewer_phone = request.POST.get('reviewer_phone', '')
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')
        
        if reviewer_name and rating:
            Review.objects.create(
                business=business,
                reviewer_name=reviewer_name,
                reviewer_phone=reviewer_phone,
                rating=rating,
                comment=comment,
                is_verified=False,
            )
            messages.success(request, 'شكراً لك! تم إرسال تقييمك وسيتم مراجعته قريباً.')
        else:
            messages.error(request, 'يرجى إدخال الاسم والتقييم.')
        
        return redirect('directory:business_detail', slug=business_slug)
    
    context = {
        'business': business,
    }
    return render(request, 'reviews/add_review.html', context)


@login_required
def edit_review(request, pk):
    """تعديل تقييم"""
    review = get_object_or_404(Review, pk=pk)
    
    # التحقق من الصلاحيات (المالك أو الأدمن)
    if not (request.user.is_staff or review.business.owner == request.user):
        messages.error(request, 'ليس لديك صلاحية لتعديل هذا التقييم.')
        return redirect('directory:business_detail', slug=review.business.slug)
    
    if request.method == 'POST':
        review.reviewer_name = request.POST.get('reviewer_name')
        review.rating = request.POST.get('rating')
        review.comment = request.POST.get('comment')
        review.save()
        
        messages.success(request, 'تم تحديث التقييم بنجاح!')
        return redirect('directory:business_detail', slug=review.business.slug)
    
    context = {
        'review': review,
    }
    return render(request, 'reviews/edit_review.html', context)


@login_required
def delete_review(request, pk):
    """حذف تقييم"""
    review = get_object_or_404(Review, pk=pk)
    
    # التحقق من الصلاحيات
    if not (request.user.is_staff or review.business.owner == request.user):
        messages.error(request, 'ليس لديك صلاحية لحذف هذا التقييم.')
        return redirect('directory:business_detail', slug=review.business.slug)
    
    if request.method == 'POST':
        business_slug = review.business.slug
        review.delete()
        messages.success(request, 'تم حذف التقييم بنجاح!')
        return redirect('directory:business_detail', slug=business_slug)
    
    context = {
        'review': review,
    }
    return render(request, 'reviews/delete_review_confirm.html', context)

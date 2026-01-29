from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Product, ProductImage
from directory.models import Business


def product_list(request, business_slug):
    """قائمة منتجات محل معين"""
    business = get_object_or_404(Business, slug=business_slug, is_active=True)
    products = Product.objects.filter(
        business=business,
        is_available=True
    ).prefetch_related('images').order_by('-created_at')
    
    context = {
        'business': business,
        'products': products,
    }
    return render(request, 'products/product_list.html', context)


def product_detail(request, pk):
    """تفاصيل منتج"""
    product = get_object_or_404(
        Product.objects.prefetch_related('images'),
        pk=pk,
        is_available=True
    )
    
    context = {
        'product': product,
    }
    return render(request, 'products/product_detail.html', context)


@login_required
def product_add(request):
    """إضافة منتج جديد"""
    # التحقق من أن المستخدم لديه محل
    businesses = Business.objects.filter(owner=request.user, is_active=True)
    
    if not businesses.exists():
        messages.error(request, 'يجب أن يكون لديك محل نشط لإضافة منتجات.')
        return redirect('directory:home')
    
    if request.method == 'POST':
        # معالجة إضافة المنتج
        business_id = request.POST.get('business')
        name = request.POST.get('name')
        description = request.POST.get('description')
        price = request.POST.get('price')
        
        business = get_object_or_404(Business, pk=business_id, owner=request.user)
        
        product = Product.objects.create(
            business=business,
            name=name,
            description=description,
            price=price,
        )
        
        messages.success(request, 'تم إضافة المنتج بنجاح!')
        return redirect('products:product_detail', pk=product.pk)
    
    context = {
        'businesses': businesses,
    }
    return render(request, 'products/product_add.html', context)


@login_required
def product_edit(request, pk):
    """تعديل منتج"""
    product = get_object_or_404(Product, pk=pk, business__owner=request.user)
    
    if request.method == 'POST':
        product.name = request.POST.get('name')
        product.description = request.POST.get('description')
        product.price = request.POST.get('price')
        product.save()
        
        messages.success(request, 'تم تحديث المنتج بنجاح!')
        return redirect('products:product_detail', pk=product.pk)
    
    context = {
        'product': product,
    }
    return render(request, 'products/product_edit.html', context)


@login_required
def product_delete(request, pk):
    """حذف منتج"""
    product = get_object_or_404(Product, pk=pk, business__owner=request.user)
    
    if request.method == 'POST':
        business_slug = product.business.slug
        product.delete()
        messages.success(request, 'تم حذف المنتج بنجاح!')
        return redirect('products:product_list', business_slug=business_slug)
    
    context = {
        'product': product,
    }
    return render(request, 'products/product_delete_confirm.html', context)

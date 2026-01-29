from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    # قائمة المنتجات لمحل معين
    path('business/<slug:business_slug>/', views.product_list, name='product_list'),
    
    # تفاصيل منتج
    path('<int:pk>/', views.product_detail, name='product_detail'),
    
    # إضافة منتج (يتطلب تسجيل دخول)
    path('add/', views.product_add, name='product_add'),
    
    # تعديل منتج
    path('<int:pk>/edit/', views.product_edit, name='product_edit'),
    
    # حذف منتج
    path('<int:pk>/delete/', views.product_delete, name='product_delete'),
]

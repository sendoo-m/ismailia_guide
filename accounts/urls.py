from django.urls import path
from .views import vendor_views
from . import views

urlpatterns = [
    # ============================================
    # AUTHENTICATION - المصادقة
    # ============================================
    path('login/', views.user_login, name='login'),
    path('register/', views.user_register, name='register'),
    path('logout/', views.user_logout, name='logout'),
    
    # ============================================
    # ADMIN DASHBOARD - لوحة المسؤولين
    # ============================================
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    
    # ──────────────────────────────────────────
    # إدارة المحلات
    # ──────────────────────────────────────────
    path('admin/businesses/', views.manage_businesses, name='manage_businesses'),
    path('admin/businesses/add/', views.add_business_admin, name='add_business_admin'),
    path('admin/businesses/<int:pk>/edit/', views.edit_business_admin, name='edit_business_admin'),
    path('admin/businesses/<int:pk>/toggle-status/', views.toggle_business_status, name='toggle_business_status'),
    path('admin/businesses/<int:pk>/toggle-verification/', views.toggle_business_verification, name='toggle_business_verification'),
    path('admin/businesses/<int:pk>/delete/', views.delete_business_admin, name='delete_business_admin'),
    
    # ──────────────────────────────────────────
    # إدارة الفئات
    # ──────────────────────────────────────────
    path('admin/categories/', views.manage_categories, name='manage_categories'),
    path('admin/categories/add/', views.add_category, name='add_category'),
    path('admin/categories/<int:pk>/edit/', views.edit_category, name='edit_category'),
    path('admin/categories/<int:pk>/delete/', views.delete_category, name='delete_category'),
    
    # ──────────────────────────────────────────
    # إدارة المحافظات والأحياء
    # ──────────────────────────────────────────
    path('admin/governorates/', views.manage_governorates, name='manage_governorates'),
    path('admin/districts/', views.manage_districts, name='manage_districts'),
    
    # ──────────────────────────────────────────
    # إدارة المستخدمين
    # ──────────────────────────────────────────
    path('admin/users/', views.manage_users, name='manage_users'),
    path('admin/users/<int:pk>/edit/', views.edit_user, name='edit_user'),
    path('admin/users/<int:pk>/delete/', views.delete_user, name='delete_user'),
    path('admin/users/<int:pk>/toggle-status/', views.toggle_user_status, name='toggle_user_status'),
    path('admin/users/<int:user_id>/businesses/', views.user_businesses, name='user_businesses'),
    
    # ──────────────────────────────────────────
    # إدارة التقييمات
    # ──────────────────────────────────────────
    path('admin/reviews/', views.manage_reviews, name='manage_reviews'),
    path('admin/reviews/<int:pk>/approve/', views.approve_review, name='approve_review'),
    path('admin/reviews/<int:pk>/delete/', views.delete_review, name='delete_review'),
    
    # ──────────────────────────────────────────
    # إدارة أصحاب المحلات (Vendors)
    # ──────────────────────────────────────────
    path('admin/vendors/add/', views.add_vendor, name='add_vendor'),
    path('admin/vendors/<int:pk>/edit/', views.edit_vendor, name='edit_vendor'),
    path('admin/vendors/<int:pk>/delete/', views.delete_vendor, name='delete_vendor'),
    path('admin/vendors/<int:pk>/toggle-status/', views.toggle_vendor_status, name='toggle_vendor_status'),
    
    # ============================================
    # VENDOR DASHBOARD - لوحة أصحاب المحلات
    # ============================================
    path('dashboard/', vendor_views.vendor_dashboard, name='vendor_dashboard'),
    
    # ──────────────────────────────────────────
    # إدارة المحل
    # ──────────────────────────────────────────
    path('business/<int:pk>/edit/', vendor_views.edit_business, name='edit_business'),
    path('business/<int:pk>/delete/', vendor_views.delete_business, name='delete_business'),
    
    # ──────────────────────────────────────────
    # إدارة المنتجات
    # ──────────────────────────────────────────
    path('products/', vendor_views.manage_products, name='manage_products'),
    path('products/add/', vendor_views.add_product, name='add_product'),
    path('products/<int:pk>/edit/', vendor_views.edit_product, name='edit_product'),
    path('products/<int:pk>/delete/', vendor_views.delete_product, name='delete_product'),
    path('products/import/', vendor_views.import_products, name='import_products'),
    
    # ──────────────────────────────────────────
    # التقارير والاشتراكات
    # ──────────────────────────────────────────
    path('reports/', vendor_views.reports, name='reports'),
    path('subscription/', vendor_views.upgrade_subscription_page, name='upgrade_subscription_page'),
    path('subscription/<int:plan_id>/upgrade/', vendor_views.upgrade_subscription, name='upgrade_subscription'),
    
    # ──────────────────────────────────────────
    # الإعدادات
    # ──────────────────────────────────────────
    path('settings/', vendor_views.dashboard_settings, name='dashboard_settings'),
]

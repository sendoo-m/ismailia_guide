"""
Views for Accounts App
======================
تنظيم الـ views حسب الوظيفة
"""

# Authentication Views
from .auth_views import (
    user_login,
    user_register,
    register_vendor,
    user_logout,
)

# Admin Views
from .admin_views import (
    admin_dashboard,
    manage_businesses,
    manage_categories,
    add_category,
    edit_category,
    delete_category,
    manage_reviews,
    approve_review,
    delete_review,
    manage_governorates,
    manage_districts,
    settings,
    get_admin_stats,  # ✅ أضف ده
    add_vendor,
    edit_vendor,
    delete_vendor,
    toggle_vendor_status,
    toggle_business_status,
    toggle_business_verification,
    delete_business_admin,
)

# Vendor Views
from .vendor_views import (
    vendor_dashboard,
    edit_business,
    manage_products,
    add_product,
    edit_product,
    delete_product,
    import_products,
    reports,
    upgrade_subscription_page,
    upgrade_subscription,
)

# User Management Views (NEW!)
from .user_management import (
    manage_users,
    edit_user,
    delete_user,
    toggle_user_status,
    user_businesses,
    edit_business_admin,
    toggle_business_status as toggle_business_admin,
    add_business_admin,
)

__all__ = [
    # Auth
    'user_login',
    'user_register',
    'register_vendor',
    'user_logout',
    
    # Admin
    'admin_dashboard',
    'manage_businesses',
    'manage_categories',
    'add_category',
    'edit_category',
    'delete_category',
    'manage_reviews',
    'approve_review',
    'delete_review',
    'manage_governorates',
    'manage_districts',
    'settings',
    'get_admin_stats',  # ✅ أضف ده
    'add_vendor',
    'edit_vendor',
    'delete_vendor',
    'toggle_vendor_status',
    'toggle_business_status',
    'toggle_business_verification',
    'delete_business_admin',
    
    # Vendor
    'vendor_dashboard',
    'edit_business',
    'manage_products',
    'add_product',
    'edit_product',
    'delete_product',
    'import_products',
    'reports',
    'upgrade_subscription_page',
    'upgrade_subscription',
    
    # User Management
    'manage_users',
    'edit_user',
    'delete_user',
    'toggle_user_status',
    'user_businesses',
    'edit_business_admin',
    'toggle_business_admin',
    'add_business_admin',
]

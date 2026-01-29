from django.urls import path
from . import views

app_name = 'subscriptions'

urlpatterns = [
    # عرض الخطط
    path('plans/', views.plans_list, name='plans_list'),
    
    # الاشتراك في خطة
    path('subscribe/<int:plan_id>/', views.subscribe, name='subscribe'),
    
    # اشتراكاتي
    path('my-subscriptions/', views.my_subscriptions, name='my_subscriptions'),
    
    # إلغاء اشتراك
    path('cancel/<int:subscription_id>/', views.cancel_subscription, name='cancel_subscription'),
]

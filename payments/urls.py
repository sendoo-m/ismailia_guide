from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    # بوابة الدفع
    path('checkout/<int:subscription_id>/', views.checkout, name='checkout'),
    
    # تأكيد الدفع
    path('confirm/<int:payment_id>/', views.payment_confirm, name='payment_confirm'),
    
    # سجل المدفوعات
    path('history/', views.payment_history, name='payment_history'),
]

from django.urls import path
from . import views

app_name = 'reviews'

urlpatterns = [
    # إضافة تقييم
    path('add/<slug:business_slug>/', views.add_review, name='add_review'),
    
    # تعديل تقييم
    path('<int:pk>/edit/', views.edit_review, name='edit_review'),
    
    # حذف تقييم
    path('<int:pk>/delete/', views.delete_review, name='delete_review'),
]

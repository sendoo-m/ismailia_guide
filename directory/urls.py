from django.urls import path
from . import views


urlpatterns = [
    # الصفحة الرئيسية
    path('', views.home, name='home'),

    # المحلات
    path('businesses/', views.business_list, name='business_list'),
    path('business/<uslug:slug>/', views.business_detail, name='business_detail'),

    # الفئات
    path('categories/', views.categories_view, name='categories'),
    path('category/<uslug:slug>/', views.category_detail, name='category_detail'),

    # الأحياء
    path('districts/', views.districts_view, name='districts'),
    path('district/<uslug:slug>/', views.district_detail, name='district_detail'),

    # المحافظات
    path('governorates/', views.governorates_view, name='governorates'),
    path('governorate/<uslug:slug>/', views.governorate_detail, name='governorate_detail'),
    path('governorate/<uslug:slug>/districts/', views.governorate_districts, name='governorate_districts'),

    # الخريطة
    path('map/', views.map_view, name='map_view'),

    # الصفحات الثابتة
    path('contact/', views.contact, name='contact'),
    path('about/', views.about, name='about'),
    path('privacy/', views.privacy, name='privacy'),
    path('terms/', views.terms, name='terms'),
    path('faq/', views.faq, name='faq'),
    
    # API
    path('api/districts/<int:governorate_id>/', 
         views.get_districts_by_governorate, 
         name='get_districts'),

    
    # صفحات المحافظات والأحياء
    path('governorates/', views.governorates, name='governorates'),
    path('governorate/<slug:slug>/', views.governorate_detail, name='governorate_detail'),
    path('district/<slug:slug>/', views.district_detail, name='district_detail'),
    

]

from django.core.management.base import BaseCommand
from subscriptions.models import SubscriptionPlan
from decimal import Decimal


class Command(BaseCommand):
    help = 'تحميل خطط الاشتراك'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('💰 بدء تحميل خطط الاشتراك...'))
        
        plans_data = [
            {
                'name': 'free',
                'display_name': 'خطة مجانية',
                'price_yearly': Decimal('0.00'),
                'max_products': 5,
                'can_upload_images': False,
                'show_prices': False,
                'has_delivery_options': False,
                'featured_in_search': False,
                'description': '''
                    ✅ معلومات أساسية عن المحل
                    ✅ إضافة حتى 5 منتجات/خدمات
                    ✅ رقم الهاتف والعنوان
                    ❌ بدون صور للمنتجات
                    ❌ بدون عرض الأسعار
                    ❌ بدون خيارات التوصيل
                ''',
                'is_active': True
            },
            {
                'name': 'basic',
                'display_name': 'خطة أساسية',
                'price_yearly': Decimal('500.00'),
                'max_products': 20,
                'can_upload_images': True,
                'show_prices': True,
                'has_delivery_options': False,
                'featured_in_search': False,
                'description': '''
                    ✅ كل مميزات الخطة المجانية
                    ✅ إضافة حتى 20 منتج/خدمة
                    ✅ رفع صور للمنتجات
                    ✅ عرض الأسعار
                    ✅ لوجو المحل
                    ✅ ساعات العمل
                    ❌ بدون أولوية في نتائج البحث
                    ❌ بدون خيارات التوصيل
                ''',
                'is_active': True
            },
            {
                'name': 'premium',
                'display_name': 'خطة مميزة',
                'price_yearly': Decimal('1200.00'),
                'max_products': 50,
                'can_upload_images': True,
                'show_prices': True,
                'has_delivery_options': True,
                'featured_in_search': True,
                'description': '''
                    ✅ كل مميزات الخطة الأساسية
                    ✅ إضافة حتى 50 منتج/خدمة
                    ✅ أولوية في نتائج البحث
                    ✅ شارة "محل مميز"
                    ✅ خيارات التوصيل والأسعار
                    ✅ معرض صور للمحل
                    ✅ روابط السوشيال ميديا
                    ✅ موقع على الخريطة
                ''',
                'is_active': True
            },
            {
                'name': 'vip',
                'display_name': 'خطة VIP',
                'price_yearly': Decimal('2500.00'),
                'max_products': 0,  # غير محدود
                'can_upload_images': True,
                'show_prices': True,
                'has_delivery_options': True,
                'featured_in_search': True,
                'description': '''
                    ✅ كل مميزات الخطة المميزة
                    ✅ عدد منتجات غير محدود
                    ✅ أولوية قصوى في نتائج البحث
                    ✅ شارة "VIP" ذهبية
                    ✅ ظهور في الصفحة الرئيسية
                    ✅ إعلانات مميزة
                    ✅ تقارير وإحصائيات متقدمة
                    ✅ دعم فني مباشر
                    ✅ صور ومقاطع فيديو غير محدودة
                ''',
                'is_active': True
            },
        ]
        
        created_count = 0
        updated_count = 0
        
        for plan_data in plans_data:
            plan, created = SubscriptionPlan.objects.update_or_create(
                name=plan_data['name'],
                defaults={
                    'display_name': plan_data['display_name'],
                    'price_yearly': plan_data['price_yearly'],
                    'max_products': plan_data['max_products'],
                    'can_upload_images': plan_data['can_upload_images'],
                    'show_prices': plan_data['show_prices'],
                    'has_delivery_options': plan_data['has_delivery_options'],
                    'featured_in_search': plan_data['featured_in_search'],
                    'description': plan_data['description'].strip(),
                    'is_active': plan_data['is_active'],
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'  ✅ تم إنشاء: {plan.display_name} - {plan.price_yearly} جنيه'))
            else:
                updated_count += 1
                self.stdout.write(self.style.WARNING(f'  🔄 تم تحديث: {plan.display_name} - {plan.price_yearly} جنيه'))
        
        self.stdout.write(self.style.SUCCESS('\n' + '='*60))
        self.stdout.write(self.style.SUCCESS('✅ تم تحميل خطط الاشتراك بنجاح!'))
        self.stdout.write(self.style.SUCCESS('='*60))
        self.stdout.write(self.style.SUCCESS(f'📊 تم إنشاء: {created_count} خطة'))
        self.stdout.write(self.style.SUCCESS(f'🔄 تم تحديث: {updated_count} خطة'))
        self.stdout.write(self.style.SUCCESS(f'📦 إجمالي الخطط: {SubscriptionPlan.objects.count()}'))
        self.stdout.write(self.style.SUCCESS('='*60))

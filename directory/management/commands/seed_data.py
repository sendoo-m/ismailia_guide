from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from directory.models import Category, District, Business
from subscriptions.models import SubscriptionPlan, Subscription
from django.utils import timezone
from datetime import timedelta

User = get_user_model()


class Command(BaseCommand):
    help = 'إضافة بيانات تجريبية للمشروع'

    def handle(self, *args, **options):
        self.stdout.write('🌱 جاري إضافة البيانات التجريبية...\n')
        
        # 1. إنشاء Superuser
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@ismailia-guide.com',
                password='admin123',
                phone='01234567890'
            )
            self.stdout.write(self.style.SUCCESS('✅ تم إنشاء Admin'))
        
        # 2. إنشاء Vendor
        if not User.objects.filter(username='vendor').exists():
            vendor = User.objects.create_user(
                username='vendor',
                email='vendor@example.com',
                password='vendor123',
                phone='01111111111',
                user_type='vendor'
            )
            self.stdout.write(self.style.SUCCESS('✅ تم إنشاء Vendor'))
        else:
            vendor = User.objects.get(username='vendor')
        
        # 3. إنشاء الفئات
        categories_data = [
            {'name': 'مطاعم ومقاهي', 'icon': 'fas fa-utensils', 'order': 1},
            {'name': 'صيدليات', 'icon': 'fas fa-pills', 'order': 2},
            {'name': 'محلات ملابس', 'icon': 'fas fa-tshirt', 'order': 3},
            {'name': 'خدمات طبية', 'icon': 'fas fa-stethoscope', 'order': 4},
            {'name': 'محلات إلكترونيات', 'icon': 'fas fa-laptop', 'order': 5},
            {'name': 'سوبر ماركت', 'icon': 'fas fa-shopping-cart', 'order': 6},
        ]
        
        for cat_data in categories_data:
            Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={
                    'icon': cat_data['icon'],
                    'order': cat_data['order'],
                    'is_active': True
                }
            )
        self.stdout.write(self.style.SUCCESS(f'✅ تم إنشاء {len(categories_data)} فئة'))
        
        # 4. إنشاء الأحياء
        districts_data = [
            'التل الكبير',
            'الشيخ زايد',
            'الأفنيوز',
            'القنطرة غرب',
            'أبو صوير',
        ]
        
        for district_name in districts_data:
            District.objects.get_or_create(
                name=district_name,
                defaults={'is_active': True}
            )
        self.stdout.write(self.style.SUCCESS(f'✅ تم إنشاء {len(districts_data)} حي'))
        
        # 5. إنشاء خطط الاشتراك
        plans_data = [
            {
                'name': 'free',
                'display_name': 'مجاني',
                'price_yearly': 0,
                'max_products': 5,
                'can_upload_images': False,
                'show_prices': False,
            },
            {
                'name': 'basic',
                'display_name': 'أساسي',
                'price_yearly': 500,
                'max_products': 50,
                'can_upload_images': True,
                'show_prices': True,
            },
            {
                'name': 'premium',
                'display_name': 'مميز',
                'price_yearly': 1200,
                'max_products': 200,
                'can_upload_images': True,
                'show_prices': True,
                'has_delivery_options': True,
                'featured_in_search': True,
            },
            {
                'name': 'vip',
                'display_name': 'VIP',
                'price_yearly': 2500,
                'max_products': 0,  # غير محدود
                'can_upload_images': True,
                'show_prices': True,
                'has_delivery_options': True,
                'featured_in_search': True,
            },
        ]
        
        for plan_data in plans_data:
            SubscriptionPlan.objects.get_or_create(
                name=plan_data['name'],
                defaults=plan_data
            )
        self.stdout.write(self.style.SUCCESS(f'✅ تم إنشاء {len(plans_data)} خطة اشتراك'))
        
        # 6. إنشاء محل تجريبي
        category = Category.objects.first()
        district = District.objects.first()
        free_plan = SubscriptionPlan.objects.get(name='free')
        
        if not Business.objects.filter(owner=vendor).exists():
            business = Business.objects.create(
                owner=vendor,
                name='محل تجريبي',
                category=category,
                district=district,
                phone='01234567890',
                whatsapp='01234567890',
                email='test@example.com',
                address='عنوان تجريبي، الإسماعيلية',
                description='هذا محل تجريبي للاختبار',
                working_hours='السبت-الخميس: 9 صباحاً - 10 مساءً',
                is_active=True,
                is_verified=True,
            )
            
            # إنشاء اشتراك
            Subscription.objects.create(
                business=business,
                plan=free_plan,
                start_date=timezone.now(),
                end_date=timezone.now() + timedelta(days=365),
                status='active'
            )
            
            self.stdout.write(self.style.SUCCESS('✅ تم إنشاء محل تجريبي'))
        
        self.stdout.write(self.style.SUCCESS('\n🎉 تم إضافة جميع البيانات التجريبية بنجاح!'))
        self.stdout.write('\n📝 بيانات الدخول:')
        self.stdout.write('   Admin: username=admin, password=admin123')
        self.stdout.write('   Vendor: username=vendor, password=vendor123')

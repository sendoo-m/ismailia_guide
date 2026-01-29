from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from directory.models import Category, District, Business
from subscriptions.models import SubscriptionPlan, Subscription
from products.models import Product
from reviews.models import Review

User = get_user_model()

class Command(BaseCommand):
    help = 'ملء قاعدة البيانات ببيانات تجريبية'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('🚀 بدء إضافة البيانات التجريبية...'))
        
        # 1. إنشاء المستخدمين
        self.create_users()
        
        # 2. إنشاء الفئات
        self.create_categories()
        
        # 3. إنشاء الأحياء
        self.create_districts()
        
        # 4. إنشاء خطط الاشتراك
        self.create_subscription_plans()
        
        # 5. إنشاء المحلات
        self.create_businesses()
        
        # 6. إنشاء المنتجات
        self.create_products()
        
        # 7. إنشاء التقييمات
        self.create_reviews()
        
        self.stdout.write(self.style.SUCCESS('✅ تم إضافة جميع البيانات بنجاح!'))

    def create_users(self):
        self.stdout.write('📝 إنشاء المستخدمين...')
        
        # Vendors
        vendors_data = [
            {'username': 'ahmed_resto', 'email': 'ahmed@resto.com', 'phone': '01012345678'},
            {'username': 'mohamed_pharmacy', 'email': 'mohamed@pharmacy.com', 'phone': '01023456789'},
            {'username': 'fatma_clothes', 'email': 'fatma@clothes.com', 'phone': '01034567890'},
            {'username': 'sara_cafe', 'email': 'sara@cafe.com', 'phone': '01045678901'},
            {'username': 'ali_electronics', 'email': 'ali@electronics.com', 'phone': '01056789012'},
        ]
        
        for data in vendors_data:
            user, created = User.objects.get_or_create(
                username=data['username'],
                defaults={
                    'email': data['email'],
                    'phone': data['phone'],
                    'user_type': 'vendor',
                    'is_verified': True
                }
            )
            if created:
                user.set_password('password123')
                user.save()
                self.stdout.write(f'  ✓ تم إنشاء: {user.username}')

    def create_categories(self):
        self.stdout.write('📂 إنشاء الفئات...')
        
        categories_data = [
            {'name': 'مطاعم ومقاهي', 'icon': 'fa-utensils', 'order': 1},
            {'name': 'صيدليات', 'icon': 'fa-pills', 'order': 2},
            {'name': 'ملابس وأزياء', 'icon': 'fa-shirt', 'order': 3},
            {'name': 'إلكترونيات', 'icon': 'fa-mobile-screen', 'order': 4},
            {'name': 'عيادات ومراكز طبية', 'icon': 'fa-stethoscope', 'order': 5},
            {'name': 'ورش وصيانة', 'icon': 'fa-wrench', 'order': 6},
            {'name': 'عقارات', 'icon': 'fa-building', 'order': 7},
            {'name': 'تعليم ودورات', 'icon': 'fa-graduation-cap', 'order': 8},
            {'name': 'بقالة وسوبر ماركت', 'icon': 'fa-cart-shopping', 'order': 9},
            {'name': 'خدمات منزلية', 'icon': 'fa-house', 'order': 10},
        ]
        
        for data in categories_data:
            category, created = Category.objects.get_or_create(
                name=data['name'],
                defaults={
                    'icon': data['icon'],
                    'order': data['order'],
                    'description': f'جميع الخدمات والمحلات المتعلقة بـ {data["name"]}'
                }
            )
            if created:
                self.stdout.write(f'  ✓ تم إنشاء الفئة: {category.name}')

    def create_districts(self):
        self.stdout.write('🏘️ إنشاء الأحياء...')
        
        districts_data = [
            'الشيخ زايد',
            'التل الكبير',
            'القنطرة شرق',
            'القنطرة غرب',
            'فايد',
            'الإسماعيلية الجديدة',
            'حي السلام',
            'حي المناخ',
            'حي الأفنيو',
            'أبو صوير',
        ]
        
        for name in districts_data:
            district, created = District.objects.get_or_create(
                name=name,
                defaults={'description': f'حي {name} - محافظة الإسماعيلية'}
            )
            if created:
                self.stdout.write(f'  ✓ تم إنشاء الحي: {district.name}')

    def create_subscription_plans(self):
        self.stdout.write('💳 إنشاء خطط الاشتراك...')
        
        plans_data = [
            {
                'name': 'free',
                'display_name': 'مجاني',
                'price_yearly': Decimal('0.00'),
                'max_products': 5,
                'can_upload_images': False,
                'show_prices': False,
                'has_delivery_options': False,
                'featured_in_search': False,
                'description': 'خطة مجانية للتجربة'
            },
            {
                'name': 'basic',
                'display_name': 'أساسي',
                'price_yearly': Decimal('500.00'),
                'max_products': 20,
                'can_upload_images': True,
                'show_prices': True,
                'has_delivery_options': False,
                'featured_in_search': False,
                'description': 'مناسبة للمحلات الصغيرة'
            },
            {
                'name': 'premium',
                'display_name': 'مميز',
                'price_yearly': Decimal('1200.00'),
                'max_products': 100,
                'can_upload_images': True,
                'show_prices': True,
                'has_delivery_options': True,
                'featured_in_search': True,
                'description': 'مثالية للمحلات المتوسطة'
            },
            {
                'name': 'vip',
                'display_name': 'VIP',
                'price_yearly': Decimal('2500.00'),
                'max_products': 0,  # unlimited
                'can_upload_images': True,
                'show_prices': True,
                'has_delivery_options': True,
                'featured_in_search': True,
                'description': 'جميع المميزات للمحلات الكبيرة'
            },
        ]
        
        for data in plans_data:
            plan, created = SubscriptionPlan.objects.get_or_create(
                name=data['name'],
                defaults=data
            )
            if created:
                self.stdout.write(f'  ✓ تم إنشاء خطة: {plan.display_name}')

    def create_businesses(self):
        self.stdout.write('🏪 إنشاء المحلات...')
        
        businesses_data = [
            {
                'owner': 'ahmed_resto',
                'name': 'مطعم الأصالة',
                'category': 'مطاعم ومقاهي',
                'district': 'الشيخ زايد',
                'phone': '01012345678',
                'whatsapp': '01012345678',
                'address': 'شارع الجيش، بجوار مسجد الفتح',
                'description': 'مطعم متخصص في المأكولات المصرية والشرقية، نقدم أطباق طازجة ولذيذة',
                'working_hours': 'السبت-الخميس: 10 ص - 12 م\nالجمعة: 2 ظ - 12 م',
                'latitude': Decimal('30.5833'),
                'longitude': Decimal('32.2667'),
                'plan': 'premium'
            },
            {
                'owner': 'mohamed_pharmacy',
                'name': 'صيدلية النور',
                'category': 'صيدليات',
                'district': 'التل الكبير',
                'phone': '01023456789',
                'address': 'شارع سعد زغلول، أمام البنك الأهلي',
                'description': 'صيدلية متكاملة توفر جميع أنواع الأدوية ومستحضرات التجميل',
                'working_hours': 'يومياً: 8 ص - 2 ص',
                'latitude': Decimal('30.5900'),
                'longitude': Decimal('32.2700'),
                'plan': 'basic'
            },
            {
                'owner': 'fatma_clothes',
                'name': 'بوتيك الأناقة',
                'category': 'ملابس وأزياء',
                'district': 'حي الأفنيو',
                'phone': '01034567890',
                'whatsapp': '01034567890',
                'address': 'الأفنيو مول، الطابق الثاني',
                'description': 'أحدث صيحات الموضة للسيدات والبنات، ملابس محجبات وإكسسوارات',
                'working_hours': 'يومياً: 10 ص - 11 م',
                'latitude': Decimal('30.5950'),
                'longitude': Decimal('32.2750'),
                'plan': 'vip'
            },
            {
                'owner': 'sara_cafe',
                'name': 'كافيه سارة',
                'category': 'مطاعم ومقاهي',
                'district': 'حي المناخ',
                'phone': '01045678901',
                'address': 'كورنيش الإسماعيلية، بجوار نادي القناة',
                'description': 'كافيه عصري يقدم أفضل أنواع القهوة والمشروبات الساخنة والباردة',
                'working_hours': 'يومياً: 3 ظ - 2 ص',
                'latitude': Decimal('30.5880'),
                'longitude': Decimal('32.2680'),
                'plan': 'premium'
            },
            {
                'owner': 'ali_electronics',
                'name': 'محل علي للإلكترونيات',
                'category': 'إلكترونيات',
                'district': 'حي السلام',
                'phone': '01056789012',
                'whatsapp': '01056789012',
                'address': 'شارع صلاح سالم، بجوار كارفور',
                'description': 'بيع وصيانة جميع أنواع الإلكترونيات والهواتف المحمولة',
                'working_hours': 'السبت-الخميس: 9 ص - 10 م',
                'latitude': Decimal('30.5820'),
                'longitude': Decimal('32.2720'),
                'plan': 'basic'
            },
        ]
        
        for data in businesses_data:
            owner = User.objects.get(username=data['owner'])
            category = Category.objects.get(name=data['category'])
            district = District.objects.get(name=data['district'])
            plan = SubscriptionPlan.objects.get(name=data['plan'])
            
            business, created = Business.objects.get_or_create(
                name=data['name'],
                defaults={
                    'owner': owner,
                    'category': category,
                    'district': district,
                    'phone': data['phone'],
                    'whatsapp': data.get('whatsapp', ''),
                    'address': data['address'],
                    'description': data['description'],
                    'working_hours': data['working_hours'],
                    'latitude': data['latitude'],
                    'longitude': data['longitude'],
                    'is_verified': True,
                    'is_active': True
                }
            )
            
            if created:
                # إنشاء اشتراك للمحل
                Subscription.objects.create(
                    business=business,
                    plan=plan,
                    start_date=timezone.now(),
                    end_date=timezone.now() + timedelta(days=365),
                    status='active'
                )
                self.stdout.write(f'  ✓ تم إنشاء: {business.name}')

    def create_products(self):
        self.stdout.write('📦 إنشاء المنتجات...')
        
        products_data = [
            # مطعم الأصالة
            {
                'business': 'مطعم الأصالة',
                'products': [
                    {'name': 'كفتة مشوية', 'price': Decimal('85.00'), 'description': 'كفتة لحم مشوية على الفحم مع أرز وسلطة'},
                    {'name': 'فراخ بانيه', 'price': Decimal('75.00'), 'description': 'فراخ بانيه مقرمشة مع بطاطس محمرة'},
                    {'name': 'مكرونة بشاميل', 'price': Decimal('60.00'), 'description': 'مكرونة باللحم المفروم والبشاميل'},
                    {'name': 'شاورما فراخ', 'price': Decimal('45.00'), 'description': 'ساندويتش شاورما فراخ مع الثوم والمخلل'},
                    {'name': 'سلطة يونانية', 'price': Decimal('30.00'), 'description': 'سلطة طازجة بالجبنة الفيتا'},
                ]
            },
            # صيدلية النور
            {
                'business': 'صيدلية النور',
                'products': [
                    {'name': 'فيتامين سي 1000', 'price': Decimal('120.00'), 'description': 'فيتامين سي فوار لتقوية المناعة'},
                    {'name': 'كريم مرطب', 'price': Decimal('85.00'), 'description': 'كريم مرطب للبشرة الجافة'},
                    {'name': 'شامبو طبي', 'price': Decimal('95.00'), 'description': 'شامبو طبي لعلاج قشرة الشعر'},
                ]
            },
            # بوتيك الأناقة
            {
                'business': 'بوتيك الأناقة',
                'products': [
                    {'name': 'عباية سوداء', 'price': Decimal('450.00'), 'description': 'عباية شيفون أسود بتطريز ذهبي', 'has_delivery': True},
                    {'name': 'طرحة حرير', 'price': Decimal('180.00'), 'description': 'طرحة حرير طبيعي بألوان متعددة', 'has_delivery': True},
                    {'name': 'فستان سواريه', 'price': Decimal('850.00'), 'description': 'فستان سهرة فخم للمناسبات', 'has_delivery': True},
                ]
            },
            # كافيه سارة
            {
                'business': 'كافيه سارة',
                'products': [
                    {'name': 'كابتشينو', 'price': Decimal('35.00'), 'description': 'كابتشينو إيطالي أصلي'},
                    {'name': 'آيس لاتيه', 'price': Decimal('40.00'), 'description': 'قهوة باردة بالحليب والثلج'},
                    {'name': 'عصير فراولة', 'price': Decimal('30.00'), 'description': 'عصير فراولة طبيعي طازج'},
                    {'name': 'كيك شوكولاتة', 'price': Decimal('45.00'), 'description': 'قطعة كيك شوكولاتة غنية'},
                ]
            },
            # محل علي للإلكترونيات
            {
                'business': 'محل علي للإلكترونيات',
                'products': [
                    {'name': 'سماعة بلوتوث', 'price': Decimal('250.00'), 'description': 'سماعة لاسلكية عالية الجودة'},
                    {'name': 'شاحن سريع', 'price': Decimal('150.00'), 'description': 'شاحن سريع 65 واط'},
                    {'name': 'كابل USB-C', 'price': Decimal('80.00'), 'description': 'كابل شحن ونقل بيانات متين'},
                ]
            },
        ]
        
        for data in products_data:
            business = Business.objects.get(name=data['business'])
            
            for product_data in data['products']:
                product, created = Product.objects.get_or_create(
                    business=business,
                    name=product_data['name'],
                    defaults={
                        'description': product_data['description'],
                        'price': product_data['price'],
                        'has_delivery': product_data.get('has_delivery', False),
                        'is_available': True
                    }
                )
                if created:
                    self.stdout.write(f'  ✓ {product.name} - {business.name}')

    def create_reviews(self):
        self.stdout.write('⭐ إنشاء التقييمات...')
        
        reviews_data = [
            {
                'business': 'مطعم الأصالة',
                'reviews': [
                    {'name': 'محمد أحمد', 'rating': 5, 'comment': 'أكل ممتاز والخدمة سريعة، المكان نظيف جداً'},
                    {'name': 'نورا سعيد', 'rating': 4, 'comment': 'الطعم حلو بس الأسعار غالية شوية'},
                    {'name': 'خالد علي', 'rating': 5, 'comment': 'أحسن مطعم في الإسماعيلية، بنروحله كل أسبوع'},
                ]
            },
            {
                'business': 'صيدلية النور',
                'reviews': [
                    {'name': 'فاطمة حسن', 'rating': 5, 'comment': 'صيدلية ممتازة والصيدلي محترم جداً'},
                    {'name': 'أحمد سمير', 'rating': 4, 'comment': 'الأدوية متوفرة والأسعار كويسة'},
                ]
            },
            {
                'business': 'بوتيك الأناقة',
                'reviews': [
                    {'name': 'سارة محمود', 'rating': 5, 'comment': 'ملابس شيك جداً وموضة، البائعة ذوقها عالي'},
                    {'name': 'هدى عبدالله', 'rating': 5, 'comment': 'اشتريت عباية وفستان، جودة ممتازة'},
                ]
            },
            {
                'business': 'كافيه سارة',
                'reviews': [
                    {'name': 'عمر يوسف', 'rating': 4, 'comment': 'القهوة لذيذة والمكان هادي'},
                    {'name': 'منى إبراهيم', 'rating': 5, 'comment': 'أحلى كافيه في الإسماعيلية، الديكور تحفة'},
                ]
            },
        ]
        
        for data in reviews_data:
            business = Business.objects.get(name=data['business'])
            
            for review_data in data['reviews']:
                review, created = Review.objects.get_or_create(
                    business=business,
                    reviewer_name=review_data['name'],
                    defaults={
                        'rating': review_data['rating'],
                        'comment': review_data['comment'],
                        'is_verified': True
                    }
                )
                if created:
                    self.stdout.write(f'  ✓ تقييم من {review.reviewer_name} لـ {business.name}')

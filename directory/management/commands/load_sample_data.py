from django.core.management.base import BaseCommand
from django.utils.text import slugify
from directory.models import Governorate, District, Category, Business, BusinessImage
from accounts.models import User
from reviews.models import Review
from products.models import Product, ProductImage
import random
from decimal import Decimal


class Command(BaseCommand):
    help = 'تحميل بيانات تجريبية شاملة للمشروع'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('🚀 بدء تحميل البيانات التجريبية...'))
        
        # ============================================
        # 👥 إنشاء مستخدمين تجريبيين
        # ============================================
        
        # مستخدم صاحب المحل
        demo_owner, created = User.objects.get_or_create(
            username='demo_owner',
            defaults={
                'email': 'demo@ismailia-guide.com',
                'first_name': 'صاحب',
                'last_name': 'المحل',
                'is_active': True,
                'user_type': 'vendor'
            }
        )
        if created:
            demo_owner.set_password('demo123456')
            demo_owner.save()
            self.stdout.write(self.style.SUCCESS(f'✅ تم إنشاء مستخدم: {demo_owner.username}'))
        
        # مستخدمين للتقييمات
        reviewers_data = [
            {'username': 'ahmed_ali', 'first_name': 'أحمد', 'last_name': 'علي', 'email': 'ahmed@test.com'},
            {'username': 'mohamed_hassan', 'first_name': 'محمد', 'last_name': 'حسن', 'email': 'mohamed@test.com'},
            {'username': 'fatma_ibrahim', 'first_name': 'فاطمة', 'last_name': 'إبراهيم', 'email': 'fatma@test.com'},
            {'username': 'sara_khalil', 'first_name': 'سارة', 'last_name': 'خليل', 'email': 'sara@test.com'},
            {'username': 'omar_salah', 'first_name': 'عمر', 'last_name': 'صلاح', 'email': 'omar@test.com'},
            {'username': 'nour_mahmoud', 'first_name': 'نور', 'last_name': 'محمود', 'email': 'nour@test.com'},
            {'username': 'youssef_adel', 'first_name': 'يوسف', 'last_name': 'عادل', 'email': 'youssef@test.com'},
            {'username': 'mona_said', 'first_name': 'منى', 'last_name': 'سعيد', 'email': 'mona@test.com'},
            {'username': 'heba_mahmoud', 'first_name': 'هبة', 'last_name': 'محمود', 'email': 'heba@test.com'},
            {'username': 'ali_hassan', 'first_name': 'علي', 'last_name': 'حسن', 'email': 'ali@test.com'},
        ]
        
        reviewers = []
        for reviewer_data in reviewers_data:
            reviewer, created = User.objects.get_or_create(
                username=reviewer_data['username'],
                defaults={
                    'email': reviewer_data['email'],
                    'first_name': reviewer_data['first_name'],
                    'last_name': reviewer_data['last_name'],
                    'is_active': True,
                    'user_type': 'customer'
                }
            )
            if created:
                reviewer.set_password('test123456')
                reviewer.save()
            reviewers.append(reviewer)
        
        self.stdout.write(self.style.SUCCESS(f'👥 تم إنشاء {len(reviewers)} مستخدم للتقييمات'))
        
        # ============================================
        # 🏷️ الفئات
        # ============================================
        categories_data = [
            {"name": "مطاعم وكافيهات", "icon": "fas fa-utensils", "description": "أفضل المطاعم والكافيهات", "order": 1},
            {"name": "محلات ملابس", "icon": "fas fa-tshirt", "description": "أحدث صيحات الموضة", "order": 2},
            {"name": "صيدليات", "icon": "fas fa-pills", "description": "صيدليات معتمدة", "order": 3},
            {"name": "مستشفيات وعيادات", "icon": "fas fa-hospital", "description": "رعاية صحية متميزة", "order": 4},
            {"name": "مراكز تعليمية", "icon": "fas fa-graduation-cap", "description": "مراكز تعليمية معتمدة", "order": 5},
            {"name": "سوبر ماركت", "icon": "fas fa-shopping-cart", "description": "تسوق احتياجاتك اليومية", "order": 6},
            {"name": "محلات إلكترونيات", "icon": "fas fa-mobile-alt", "description": "أحدث التكنولوجيا", "order": 7},
            {"name": "صالونات تجميل", "icon": "fas fa-cut", "description": "صالونات راقية", "order": 8},
            {"name": "مكتبات", "icon": "fas fa-book", "description": "مكتبات شاملة", "order": 9},
            {"name": "ورش سيارات", "icon": "fas fa-car", "description": "صيانة احترافية", "order": 10},
            {"name": "مخابز وحلويات", "icon": "fas fa-birthday-cake", "description": "منتجات طازجة يومياً", "order": 11},
            {"name": "محلات أحذية", "icon": "fas fa-shoe-prints", "description": "أحذية عصرية", "order": 12},
            {"name": "صالات رياضية", "icon": "fas fa-dumbbell", "description": "لياقة بدنية", "order": 13},
            {"name": "محلات أثاث", "icon": "fas fa-couch", "description": "أثاث عصري", "order": 14},
            {"name": "خدمات صيانة", "icon": "fas fa-tools", "description": "صيانة منزلية", "order": 15},
        ]
        
        categories = {}
        for cat_data in categories_data:
            cat, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={
                    'icon': cat_data['icon'],
                    'description': cat_data.get('description', ''),
                    'order': cat_data['order'],
                    'is_active': True
                }
            )
            categories[cat.name] = cat
            if created:
                self.stdout.write(self.style.SUCCESS(f'  ✅ فئة: {cat.name}'))
        
        self.stdout.write(self.style.SUCCESS(f'📦 تم إنشاء {len(categories)} فئة'))
        
        # ============================================
        # 🗺️ المحافظات
        # ============================================
        governorates_data = [
            {"name": "الإسماعيلية", "description": "محافظة الإسماعيلية - مدينة الجمال والسحر", "icon": "fas fa-water", "order": 1},
            {"name": "القاهرة", "description": "العاصمة المصرية - قلب مصر النابض", "icon": "fas fa-city", "order": 2},
            {"name": "الإسكندرية", "description": "عروس البحر المتوسط", "icon": "fas fa-ship", "order": 3},
            {"name": "الجيزة", "description": "موطن الأهرامات", "icon": "fas fa-monument", "order": 4},
            {"name": "الشرقية", "description": "أرض الزراعة والخير", "icon": "fas fa-tractor", "order": 5},
        ]
        
        governorates = {}
        for gov_data in governorates_data:
            gov, created = Governorate.objects.get_or_create(
                name=gov_data['name'],
                defaults={
                    'description': gov_data['description'],
                    'icon': gov_data['icon'],
                    'order': gov_data['order'],
                    'is_active': True
                }
            )
            governorates[gov.name] = gov
            if created:
                self.stdout.write(self.style.SUCCESS(f'  ✅ محافظة: {gov.name}'))
        
        self.stdout.write(self.style.SUCCESS(f'📍 تم إنشاء {len(governorates)} محافظة'))
        
        # ============================================
        # 🏘️ الأحياء
        # ============================================
        districts_data = {
            "الإسماعيلية": [
                "حي الأفنيو مول", "حي الشيخ زايد", "حي السلام", "حي الجامعة",
                "حي المستثمرين", "حي القنطرة شرق", "حي فايد", "حي التل الكبير"
            ],
            "القاهرة": [
                "مدينة نصر", "مصر الجديدة", "المعادي", "الزمالك",
                "وسط البلد", "المهندسين", "التجمع الخامس", "الرحاب"
            ],
            "الإسكندرية": [
                "محرم بك", "سموحة", "ستانلي", "سيدي جابر",
                "العصافرة", "المنتزه", "سيدي بشر"
            ],
            "الجيزة": [
                "الهرم", "فيصل", "الدقي", "المهندسين",
                "6 أكتوبر", "الشيخ زايد"
            ],
            "الشرقية": [
                "الزقازيق", "العاشر من رمضان", "بلبيس", "فاقوس"
            ]
        }
        
        districts = {}
        for gov_name, district_list in districts_data.items():
            if gov_name not in governorates:
                continue
            gov = governorates[gov_name]
            for district_name in district_list:
                district, created = District.objects.get_or_create(
                    name=district_name,
                    governorate=gov,
                    defaults={'is_active': True}
                )
                districts[f"{gov_name}_{district_name}"] = district
                if created:
                    self.stdout.write(self.style.SUCCESS(f'  ✅ حي: {district_name} - {gov_name}'))
        
        self.stdout.write(self.style.SUCCESS(f'🏘️ تم إنشاء {len(districts)} حي'))
        
        # ============================================
        # 🏪 المحلات مع إحداثيات حقيقية
        # ============================================
        
        # إحداثيات تجريبية لمحافظات مصر
        coordinates = {
            "الإسماعيلية": {"lat": 30.5965, "lng": 32.2715},
            "القاهرة": {"lat": 30.0444, "lng": 31.2357},
            "الإسكندرية": {"lat": 31.2001, "lng": 29.9187},
            "الجيزة": {"lat": 30.0131, "lng": 31.2089},
            "الشرقية": {"lat": 30.5833, "lng": 31.5000},
        }
        
        businesses_data = [
            # الإسماعيلية
            {"name": "مطعم الريف المصري", "gov": "الإسماعيلية", "district": "حي الأفنيو مول", "category": "مطاعم وكافيهات", "description": "مطعم متخصص في الأكلات المصرية الأصيلة - فطائر، كشري، فول، طعمية. نستخدم أجود الخامات ونقدم الطعام الطازج يومياً.", "phone": "01012345678", "whatsapp": "01012345678", "email": "alreef@example.com", "address": "بجوار الأفنيو مول - شارع الجيش", "working_hours": "السبت-الخميس: 8 صباحاً - 12 منتصف الليل\nالجمعة: 10 صباحاً - 12 منتصف الليل", "lat_offset": 0.001, "lng_offset": 0.001},
            
            {"name": "كافيه لافندر", "gov": "الإسماعيلية", "district": "حي الأفنيو مول", "category": "مطاعم وكافيهات", "description": "كافيه عصري يقدم القهوة الإيطالية والمشروبات الساخنة والباردة. جو هادئ ومريح مع إنترنت مجاني.", "phone": "01087654321", "whatsapp": "01087654321", "address": "داخل الأفنيو مول - الدور الأرضي", "working_hours": "يومياً: 9 صباحاً - 11 مساءً", "lat_offset": 0.002, "lng_offset": 0.001},
            
            {"name": "صيدلية النهضة", "gov": "الإسماعيلية", "district": "حي الأفنيو مول", "category": "صيدليات", "description": "صيدلية شاملة - أدوية، مستحضرات تجميل، منتجات أطفال. خدمة 24 ساعة مع طاقم صيادلة محترف.", "phone": "01123456789", "whatsapp": "01123456789", "email": "nahda@pharmacy.com", "address": "أمام الأفنيو مول - شارع الجيش", "working_hours": "24 ساعة - 7 أيام في الأسبوع", "lat_offset": 0.0005, "lng_offset": 0.002},
            
            {"name": "محل الأناقة للملابس", "gov": "الإسماعيلية", "district": "حي الأفنيو مول", "category": "محلات ملابس", "description": "أحدث صيحات الموضة الرجالية والحريمي - ماركات عالمية ومحلية. تشكيلة واسعة ومتنوعة بأسعار منافسة.", "phone": "01234567890", "whatsapp": "01234567890", "address": "الأفنيو مول - الدور الأول", "working_hours": "يومياً: 10 صباحاً - 10 مساءً", "lat_offset": 0.003, "lng_offset": 0.001},
            
            {"name": "هايبر وان", "gov": "الإسماعيلية", "district": "حي الأفنيو مول", "category": "سوبر ماركت", "description": "سوبر ماركت كبير - جميع المنتجات الغذائية والمنزلية بأسعار منافسة. عروض وخصومات أسبوعية.", "phone": "01098765432", "whatsapp": "01098765432", "address": "خلف الأفنيو مول", "working_hours": "يومياً: 8 صباحاً - 12 منتصف الليل", "lat_offset": -0.001, "lng_offset": 0.002},
            
            {"name": "مطعم بيتزا هت", "gov": "الإسماعيلية", "district": "حي الشيخ زايد", "category": "مطاعم وكافيهات", "description": "سلسلة مطاعم عالمية - بيتزا، باستا، مقبلات وحلويات. جودة عالمية وخدمة توصيل سريعة.", "phone": "01156789012", "whatsapp": "01156789012", "address": "كورنيش الشيخ زايد", "working_hours": "يومياً: 11 صباحاً - 1 بعد منتصف الليل", "lat_offset": 0.004, "lng_offset": -0.001},
            
            {"name": "عيادة د. أحمد السيد للأسنان", "gov": "الإسماعيلية", "district": "حي الشيخ زايد", "category": "مستشفيات وعيادات", "description": "عيادة متخصصة في طب وتجميل الأسنان - أحدث التقنيات العالمية. تقويم، زراعة، تبييض وتجميل.", "phone": "01223456789", "whatsapp": "01223456789", "email": "dr.ahmed@dental.com", "address": "برج النيل - الدور الثالث", "working_hours": "السبت-الخميس: 4 مساءً - 10 مساءً", "lat_offset": 0.005, "lng_offset": 0.002},
            
            {"name": "مركز الأمل التعليمي", "gov": "الإسماعيلية", "district": "حي الشيخ زايد", "category": "مراكز تعليمية", "description": "مركز تعليمي شامل - كورسات لغات، رياضيات، علوم لجميع المراحل. مدرسين أكفاء وشهادات معتمدة.", "phone": "01187654321", "whatsapp": "01187654321", "address": "شارع الثورة - بجوار مسجد الرحمة", "working_hours": "السبت-الخميس: 3 عصراً - 9 مساءً", "lat_offset": 0.003, "lng_offset": 0.003},
            
            {"name": "صالون فينوس للسيدات", "gov": "الإسماعيلية", "district": "حي الشيخ زايد", "category": "صالونات تجميل", "description": "صالون نسائي راقي - قص، صبغة، كوافير، مكياج، عناية بالبشرة. أحدث التقنيات وأفضل المنتجات.", "phone": "01298765432", "whatsapp": "01298765432", "address": "شارع السلام - فوق صيدلية المحبة", "working_hours": "السبت-الخميس: 10 صباحاً - 8 مساءً", "lat_offset": 0.002, "lng_offset": -0.002},
            
            {"name": "محل العز للإلكترونيات", "gov": "الإسماعيلية", "district": "حي السلام", "category": "محلات إلكترونيات", "description": "موبايلات، تابلت، لابتوب - أحدث الموديلات بأسعار منافسة مع ضمان معتمد. خدمة ما بعد البيع ممتازة.", "phone": "01134567890", "whatsapp": "01134567890", "email": "alezz@electronics.com", "address": "شارع الجلاء - أمام البنك الأهلي", "working_hours": "السبت-الخميس: 9 صباحاً - 10 مساءً", "lat_offset": -0.002, "lng_offset": 0.001},
            
            {"name": "مخبز الفرن الذهبي", "gov": "الإسماعيلية", "district": "حي السلام", "category": "مخابز وحلويات", "description": "مخبز وطاحونة - خبز طازج، فطائر، معجنات، حلويات شرقية وغربية. نستخدم أجود أنواع الدقيق.", "phone": "01245678901", "whatsapp": "01245678901", "address": "شارع 23 يوليو - بجوار مسجد النور", "working_hours": "يومياً: 6 صباحاً - 11 مساءً", "lat_offset": -0.003, "lng_offset": -0.001},
            
            {"name": "كارفور ماركت", "gov": "الإسماعيلية", "district": "حي السلام", "category": "سوبر ماركت", "description": "فرع كارفور - تشكيلة واسعة من المنتجات الغذائية والمنزلية. أسعار تنافسية وعروض مستمرة.", "phone": "01176543210", "whatsapp": "01176543210", "address": "شارع الجمهورية - مقابل محطة البنزين", "working_hours": "يومياً: 8 صباحاً - 12 منتصف الليل", "lat_offset": -0.004, "lng_offset": 0.002},
            
            {"name": "مكتبة الطالب", "gov": "الإسماعيلية", "district": "حي الجامعة", "category": "مكتبات", "description": "مكتبة شاملة - كتب جامعية، أدوات مكتبية، مذكرات، أوراق طباعة. خصومات للطلاب.", "phone": "01287654321", "whatsapp": "01287654321", "email": "student@library.com", "address": "أمام جامعة قناة السويس - بوابة 1", "working_hours": "السبت-الخميس: 9 صباحاً - 9 مساءً", "lat_offset": 0.006, "lng_offset": 0.001},
            
            {"name": "كافتيريا الجامعة", "gov": "الإسماعيلية", "district": "حي الجامعة", "category": "مطاعم وكافيهات", "description": "كافتيريا طلابية - سندوتشات، مشروبات، وجبات سريعة بأسعار مناسبة للطلاب. نظافة وجودة عالية.", "phone": "01198765432", "whatsapp": "01198765432", "address": "داخل الحرم الجامعي - بجوار المكتبة المركزية", "working_hours": "السبت-الخميس: 8 صباحاً - 6 مساءً", "lat_offset": 0.007, "lng_offset": 0.002},
            
            {"name": "محل كمبيوتك", "gov": "الإسماعيلية", "district": "حي الجامعة", "category": "محلات إلكترونيات", "description": "لابتوب، إكسسوارات كمبيوتر، صيانة وبرمجة، طباعة ونسخ. خدمات متكاملة للطلاب والموظفين.", "phone": "01209876543", "whatsapp": "01209876543", "address": "شارع الجامعة - بجوار البنك الأهلي", "working_hours": "السبت-الخميس: 10 صباحاً - 9 مساءً", "lat_offset": 0.005, "lng_offset": -0.001},
            
            # القاهرة
            {"name": "مطعم أبو شقرة", "gov": "القاهرة", "district": "مدينة نصر", "category": "مطاعم وكافيهات", "description": "سلسلة مطاعم شهيرة - مشويات، كباب، كفتة، طواجن. أشهر مطعم مشويات في مصر.", "phone": "01512345678", "whatsapp": "01512345678", "email": "aboshakra@restaurants.com", "address": "شارع مصطفى النحاس - أمام سيتي ستارز", "working_hours": "يومياً: 12 ظهراً - 2 بعد منتصف الليل", "lat_offset": 0.002, "lng_offset": 0.001},
            
            {"name": "سيتي ستارز مول", "gov": "القاهرة", "district": "مدينة نصر", "category": "محلات ملابس", "description": "أكبر مول في مصر - جميع الماركات العالمية والمحلية. سينما، مطاعم، ومحلات متنوعة.", "phone": "01587654321", "whatsapp": "01587654321", "address": "شارع عمر بن الخطاب", "working_hours": "يومياً: 10 صباحاً - 12 منتصف الليل", "lat_offset": 0.003, "lng_offset": 0.002},
            
            {"name": "صيدلية الإسعاف", "gov": "القاهرة", "district": "مدينة نصر", "category": "صيدليات", "description": "صيدلية كبرى - خدمة 24 ساعة، توصيل مجاني، جميع الأدوية متوفرة. فريق صيادلة محترف.", "phone": "01523456789", "whatsapp": "01523456789", "address": "شارع عباس العقاد - بجوار البنك", "working_hours": "24 ساعة - 7 أيام", "lat_offset": 0.001, "lng_offset": -0.001},
            
            {"name": "كافيه كورنر", "gov": "القاهرة", "district": "المعادي", "category": "مطاعم وكافيهات", "description": "كافيه راقي - إطلالة على النيل، جو هادئ ورومانسي. قهوة مميزة ومأكولات شهية.", "phone": "01534567890", "whatsapp": "01534567890", "address": "كورنيش المعادي - بجوار نادي اليخت", "working_hours": "يومياً: 9 صباحاً - 1 بعد منتصف الليل", "lat_offset": -0.002, "lng_offset": 0.003},
            
            {"name": "صالة باور جيم", "gov": "القاهرة", "district": "المعادي", "category": "صالات رياضية", "description": "صالة رياضية مجهزة بأحدث الأجهزة - أوزان، كارديو، تدريب شخصي. مدربين محترفين.", "phone": "01598765432", "whatsapp": "01598765432", "email": "powergym@fitness.com", "address": "شارع 9 - برج النخيل", "working_hours": "يومياً: 6 صباحاً - 11 مساءً", "lat_offset": -0.003, "lng_offset": 0.002},
            
            # الإسكندرية
            {"name": "مطعم سي جل", "gov": "الإسكندرية", "district": "سموحة", "category": "مطاعم وكافيهات", "description": "مطعم سي فود شهير - أسماك طازجة، جمبري، كاليماري، مأكولات بحرية. إطلالة رائعة.", "phone": "01612345678", "whatsapp": "01612345678", "address": "شارع فوزي معاذ - بجوار سموحة سيتي سنتر", "working_hours": "يومياً: 12 ظهراً - 1 بعد منتصف الليل", "lat_offset": 0.001, "lng_offset": 0.002},
            
            {"name": "جرين بلازا مول", "gov": "الإسكندرية", "district": "سموحة", "category": "سوبر ماركت", "description": "مول تجاري كبير - هايبر ماركت، محلات ملابس، مطاعم، سينما. وجهة تسوق متكاملة.", "phone": "01687654321", "whatsapp": "01687654321", "address": "شارع الحرية - مقابل نادي سموحة", "working_hours": "يومياً: 10 صباحاً - 12 منتصف الليل", "lat_offset": 0.002, "lng_offset": -0.001},
        ]
        
        # تعليقات
        positive_comments = [
            "محل ممتاز جداً! الخدمة رائعة والأسعار مناسبة. أنصح به بشدة ⭐⭐⭐⭐⭐",
            "تجربة رائعة! المنتجات عالية الجودة والموظفين محترمين جداً 👍",
            "من أفضل المحلات اللي زرتها! النظافة ممتازة والخدمة سريعة ✨",
            "محل جميل جداً، الأسعار معقولة والجودة ممتازة. هرجع تاني أكيد! 🌟",
            "خدمة ممتازة وموظفين متعاونين جداً. استمروا في التميز! 👏",
            "المكان نضيف جداً والمنتجات طازجة. تجربة تستحق التكرار 💯",
            "محل محترم جداً، الأسعار كويسة والجودة عالية. راضي جداً 😊",
            "أحلى محل! الموظفين لطيفين والخدمة سريعة. شكراً ليكم ❤️",
        ]
        
        good_comments = [
            "محل كويس، المنتجات جيدة والأسعار مناسبة. تجربة جيدة بشكل عام 👍",
            "الخدمة جيدة والمكان نضيف. الأسعار شوية عالية بس يستاهل.",
            "محل محترم، الموظفين متعاونين. ممكن يحسنوا السرعة شوية.",
            "تجربة كويسة، المنتجات جودتها جيدة. هحاول أزوره تاني.",
        ]
        
        average_comments = [
            "محل عادي، الخدمة مقبولة. في مجال للتحسين.",
            "المنتجات كويسة بس الأسعار عالية شوية.",
            "الخدمة بطيئة شوية، بس المنتجات كويسة.",
            "محل مقبول، مافيش حاجة مميزة بس ماشي.",
        ]
        
        business_count = 0
        created_businesses = []
        
        for biz_data in businesses_data:
            if biz_data['gov'] not in governorates or biz_data['gov'] not in coordinates:
                continue
            
            district_key = f"{biz_data['gov']}_{biz_data['district']}"
            if district_key not in districts:
                continue
            
            if biz_data['category'] not in categories:
                continue
            
            gov = governorates[biz_data['gov']]
            district = districts[district_key]
            category = categories[biz_data['category']]
            
            # حساب الإحداثيات
            base_coords = coordinates[biz_data['gov']]
            latitude = Decimal(str(base_coords['lat'] + biz_data.get('lat_offset', 0)))
            longitude = Decimal(str(base_coords['lng'] + biz_data.get('lng_offset', 0)))
            
            biz, created = Business.objects.get_or_create(
                name=biz_data['name'],
                district=district,
                defaults={
                    'owner': demo_owner,
                    'category': category,
                    'description': biz_data['description'],
                    'phone': biz_data['phone'],
                    'whatsapp': biz_data.get('whatsapp', ''),
                    'email': biz_data.get('email', ''),
                    'address': biz_data['address'],
                    'working_hours': biz_data['working_hours'],
                    'latitude': latitude,
                    'longitude': longitude,
                    'is_active': True,
                    'is_verified': True,
                    'is_featured': business_count % 3 == 0
                }
            )
            if created:
                business_count += 1
                created_businesses.append(biz)
                self.stdout.write(self.style.SUCCESS(
                    f'  ✅ محل: {biz.name} - {district.name} (📍 {latitude}, {longitude})'
                ))
        
        self.stdout.write(self.style.SUCCESS(f'\n🏪 تم إنشاء {business_count} محل'))
        
        # ============================================
        # 📦 المنتجات
        # ============================================
        
        products_by_category = {
            "مطاعم وكافيهات": [
                {"name": "بيتزا مارجريتا", "price": 120, "desc": "بيتزا مارجريتا كلاسيكية"},
                {"name": "باستا بالصوص الأحمر", "price": 85, "desc": "باستا بصوص الطماطم"},
                {"name": "قهوة اسبريسو", "price": 35, "desc": "قهوة اسبريسو إيطالية"},
                {"name": "كابتشينو", "price": 45, "desc": "كابتشينو بحليب كامل الدسم"},
                {"name": "عصير برتقال طازج", "price": 30, "desc": "عصير برتقال طبيعي 100%"},
            ],
            "محلات ملابس": [
                {"name": "تيشيرت قطن", "price": 150, "desc": "تيشيرت قطن 100%"},
                {"name": "بنطلون جينز", "price": 350, "desc": "بنطلون جينز عالي الجودة"},
                {"name": "فستان سواريه", "price": 800, "desc": "فستان سواريه أنيق"},
                {"name": "جاكيت شتوي", "price": 650, "desc": "جاكيت شتوي دافئ"},
            ],
            "صيدليات": [
                {"name": "باراسيتامول", "price": 15, "desc": "مسكن للألم وخافض للحرارة"},
                {"name": "فيتامين سي", "price": 45, "desc": "مكمل غذائي - فيتامين سي"},
                {"name": "كريم مرطب", "price": 85, "desc": "كريم مرطب للبشرة"},
                {"name": "شامبو", "price": 65, "desc": "شامبو للشعر"},
            ],
            "محلات إلكترونيات": [
                {"name": "سماعات بلوتوث", "price": 450, "desc": "سماعات بلوتوث لاسلكية"},
                {"name": "شاحن سريع", "price": 250, "desc": "شاحن سريع 25 واط"},
                {"name": "باور بنك", "price": 350, "desc": "باور بنك 20000 ميلي أمبير"},
                {"name": "كفر موبايل", "price": 80, "desc": "كفر حماية للموبايل"},
            ],
            "مكتبات": [
                {"name": "دفتر 100 ورقة", "price": 25, "desc": "دفتر سلك 100 ورقة"},
                {"name": "قلم جاف أزرق", "price": 5, "desc": "قلم جاف أزرق"},
                {"name": "أقلام رصاص (12 قلم)", "price": 30, "desc": "علبة أقلام رصاص"},
                {"name": "مسطرة 30 سم", "price": 10, "desc": "مسطرة بلاستيك"},
            ],
            "سوبر ماركت": [
                {"name": "أرز (كيلو)", "price": 25, "desc": "أرز مصري درجة أولى"},
                {"name": "سكر (كيلو)", "price": 30, "desc": "سكر أبيض"},
                {"name": "زيت (لتر)", "price": 55, "desc": "زيت طعام"},
                {"name": "معكرونة (باكيت)", "price": 15, "desc": "معكرونة"},
            ],
            "مخابز وحلويات": [
                {"name": "عيش فينو (كيلو)", "price": 10, "desc": "خبز فينو طازج"},
                {"name": "كرواسون (قطعة)", "price": 15, "desc": "كرواسون بالزبدة"},
                {"name": "تورتة شوكولاتة (كيلو)", "price": 250, "desc": "تورتة شوكولاتة فاخرة"},
                {"name": "بسكويت (كيلو)", "price": 80, "desc": "بسكويت سادة"},
            ],
        }
        
        product_count = 0
        for business in created_businesses:
            category_name = business.category.name
            if category_name in products_by_category:
                products_list = products_by_category[category_name]
                num_products = random.randint(3, min(5, len(products_list)))
                selected_products = random.sample(products_list, num_products)
                
                for prod_data in selected_products:
                    product, created = Product.objects.get_or_create(
                        business=business,
                        name=prod_data['name'],
                        defaults={
                            'description': prod_data['desc'],
                            'price': Decimal(str(prod_data['price'])),
                            'is_available': True,  # ✅ موجود
                            # ❌ is_active محذوف لأنه مش موجود في Model
                        }
                    )
                    if created:
                        product_count += 1
                        self.stdout.write(self.style.SUCCESS(
                            f'    📦 منتج: {product.name} - {product.price} جنيه'
                        ))
        
        self.stdout.write(self.style.SUCCESS(f'\n📦 تم إنشاء {product_count} منتج'))
        
        # ============================================
        # ⭐ التقييمات
        # ============================================
        
        review_count = 0
        for business in created_businesses:
            num_reviews = random.randint(3, 8)
            selected_reviewers = random.sample(reviewers, min(num_reviews, len(reviewers)))
            
            for reviewer in selected_reviewers:
                existing_review = Review.objects.filter(
                    business=business,
                    user=reviewer
                ).first()
                
                if existing_review:
                    continue
                
                rating = random.choices(
                    [5, 4, 3, 2, 1],
                    weights=[50, 30, 10, 7, 3],
                    k=1
                )[0]
                
                if rating == 5:
                    comment = random.choice(positive_comments)
                elif rating == 4:
                    comment = random.choice(positive_comments + good_comments)
                elif rating == 3:
                    comment = random.choice(good_comments + average_comments)
                else:
                    comment = random.choice(average_comments)
                
                try:
                    review = Review.objects.create(
                        business=business,
                        user=reviewer,
                        rating=rating,
                        comment=comment,
                        is_approved=True  # ✅ صح
                    )
                    review_count += 1
                except Exception as e:
                    pass
        
        self.stdout.write(self.style.SUCCESS(f'\n⭐ تم إنشاء {review_count} تقييم'))
        
        # ============================================
        # 📊 ملخص النتائج
        # ============================================
        self.stdout.write(self.style.SUCCESS('\n' + '='*60))
        self.stdout.write(self.style.SUCCESS('🎉 تم تحميل البيانات بنجاح!'))
        self.stdout.write(self.style.SUCCESS('='*60))
        self.stdout.write(self.style.SUCCESS(f'👥 المستخدمين: {User.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'📍 المحافظات: {Governorate.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'🏘️ الأحياء: {District.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'🏷️ الفئات: {Category.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'🏪 المحلات: {Business.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'📦 المنتجات: {Product.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'⭐ التقييمات: {Review.objects.count()}'))
        self.stdout.write(self.style.SUCCESS('='*60))
        self.stdout.write(self.style.WARNING('\n💡 بيانات الدخول التجريبية:'))
        self.stdout.write(self.style.WARNING('   صاحب المحل:'))
        self.stdout.write(self.style.WARNING('   Username: demo_owner'))
        self.stdout.write(self.style.WARNING('   Password: demo123456'))
        self.stdout.write(self.style.WARNING('\n   المستخدمين:'))
        self.stdout.write(self.style.WARNING('   ahmed_ali, mohamed_hassan, ...'))
        self.stdout.write(self.style.WARNING('   Password: test123456'))
        self.stdout.write(self.style.SUCCESS('='*60))

from django.core.management.base import BaseCommand
from django.core.management import call_command
from directory.models import Governorate, District, Category, Business, BusinessImage
from accounts.models import User
from reviews.models import Review
from products.models import Product, ProductImage


class Command(BaseCommand):
    help = 'حذف كل البيانات التجريبية وإعادة تحميلها'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('⚠️ جاري حذف جميع البيانات التجريبية...'))
        
        # حذف البيانات (بالترتيب العكسي للعلاقات)
        Review.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('✅ تم حذف التقييمات'))
        
        ProductImage.objects.all().delete()
        Product.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('✅ تم حذف المنتجات'))
        
        BusinessImage.objects.all().delete()
        Business.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('✅ تم حذف المحلات'))
        
        District.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('✅ تم حذف الأحياء'))
        
        Governorate.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('✅ تم حذف المحافظات'))
        
        Category.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('✅ تم حذف الفئات'))
        
        # حذف المستخدمين التجريبيين فقط (ما عدا الـ superuser)
        User.objects.filter(username__startswith='demo_').delete()
        User.objects.filter(username__in=[
            'ahmed_ali', 'mohamed_hassan', 'fatma_ibrahim', 'sara_khalil',
            'omar_salah', 'nour_mahmoud', 'youssef_adel', 'mona_said',
            'heba_mahmoud', 'ali_hassan'
        ]).delete()
        self.stdout.write(self.style.SUCCESS('✅ تم حذف المستخدمين التجريبيين'))
        
        self.stdout.write(self.style.SUCCESS('\n🔄 جاري تحميل البيانات الجديدة...\n'))
        
        # استدعاء أمر التحميل
        call_command('load_demo_data')
        
        self.stdout.write(self.style.SUCCESS('\n✅ تم إعادة تحميل البيانات بنجاح!'))

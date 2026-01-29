from django.core.management.base import BaseCommand
from directory.models import Governorate, District


class Command(BaseCommand):
    help = 'إضافة المحافظات والأحياء'
    
    def handle(self, *args, **kwargs):
        governorates_data = [
            {
                'name': 'الإسماعيلية',
                'order': 1,
                'icon': 'fas fa-landmark',
                'description': 'محافظة الإسماعيلية - مدينة القناة',
                'districts': ['التل الكبير', 'فايد', 'القنطرة شرق', 'القنطرة غرب', 'أبو صوير']
            },
            {
                'name': 'الشرقية',
                'order': 2,
                'icon': 'fas fa-city',
                'description': 'محافظة الشرقية',
                'districts': ['العاشر من رمضان', 'الزقازيق', 'بلبيس', 'فاقوس', 'ههيا']
            },
            {
                'name': 'بورسعيد',
                'order': 3,
                'icon': 'fas fa-ship',
                'description': 'محافظة بورسعيد',
                'districts': ['حي الشرق', 'حي العرب', 'حي الضواحي', 'حي المناخ']
            },
            {
                'name': 'السويس',
                'order': 4,
                'icon': 'fas fa-anchor',
                'description': 'محافظة السويس',
                'districts': ['حي السويس', 'حي الأربعين', 'حي عتاقة', 'حي الجناين']
            },
        ]
        
        for gov_data in governorates_data:
            districts = gov_data.pop('districts')
            governorate, created = Governorate.objects.get_or_create(
                name=gov_data['name'],
                defaults=gov_data
            )
            
            if created:
                self.stdout.write(self.style.SUCCESS(f'✅ محافظة: {governorate.name}'))
            
            for district_name in districts:
                district, created = District.objects.get_or_create(
                    governorate=governorate,
                    name=district_name
                )
                if created:
                    self.stdout.write(f'  ✓ {district_name}')
        
        self.stdout.write(self.style.SUCCESS('\n🎉 تم بنجاح!'))

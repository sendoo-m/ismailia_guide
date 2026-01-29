# directory/migrations/0003_governorate_support.py
# أو
# directory/migrations/0004_governorate_support.py

from django.db import migrations, models
import django.db.models.deletion


def create_ismailia_governorate(apps, schema_editor):
    """إنشاء محافظة الإسماعيلية وربط الأحياء بها"""
    Governorate = apps.get_model('directory', 'Governorate')
    District = apps.get_model('directory', 'District')
    
    # إنشاء الإسماعيلية
    ismailia = Governorate.objects.create(
        id=1,
        name='الإسماعيلية',
        slug='الإسماعيلية',
        order=1,
        is_active=True,
        description='محافظة الإسماعيلية - مدينة القناة'
    )
    
    # ربط الأحياء
    district_count = District.objects.all().update(governorate=ismailia)
    print(f"✅ تم ربط {district_count} حي بالمحافظة")


class Migration(migrations.Migration):

    dependencies = [
        # ⚠️ غيّر هنا لآخر migration موجود عندك!
        ('directory', '0002_category_created_at_category_updated_at_and_more'),
        # أو
        # ('directory', '0003_xxxx'),
    ]

    operations = [
        # إنشاء Governorate
        migrations.CreateModel(
            name='Governorate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, help_text='مثال: الإسماعيلية، الشرقية، بورسعيد', max_length=100, unique=True, verbose_name='اسم المحافظة')),
                ('slug', models.SlugField(allow_unicode=True, blank=True, max_length=100, unique=True, verbose_name='الرابط')),
                ('description', models.TextField(blank=True, help_text='معلومات عن المحافظة (اختياري)', verbose_name='الوصف')),
                ('icon', models.CharField(blank=True, help_text='مثال: fas fa-city', max_length=50, verbose_name='أيقونة Font Awesome')),
                ('is_active', models.BooleanField(default=True, help_text='إلغاء التفعيل يخفي المحافظة من الموقع', verbose_name='نشط')),
                ('order', models.IntegerField(default=0, help_text='رقم أصغر = يظهر أولاً', verbose_name='الترتيب')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='تاريخ التحديث')),
            ],
            options={
                'verbose_name': 'محافظة',
                'verbose_name_plural': 'المحافظات',
                'ordering': ['order', 'name'],
            },
        ),
        
        # Indexes
        migrations.AddIndex(
            model_name='governorate',
            index=models.Index(fields=['slug'], name='dir_gov_slug'),
        ),
        migrations.AddIndex(
            model_name='governorate',
            index=models.Index(fields=['is_active', 'order'], name='dir_gov_active'),
        ),
        
        # إضافة governorate للـ District (nullable)
        migrations.AddField(
            model_name='district',
            name='governorate',
            field=models.ForeignKey(
                blank=True, null=True,
                help_text='المحافظة التابع لها الحي',
                on_delete=django.db.models.deletion.PROTECT,
                related_name='districts',
                to='directory.governorate',
                verbose_name='المحافظة'
            ),
        ),
        
        # ملء البيانات
        migrations.RunPython(create_ismailia_governorate, migrations.RunPython.noop),
        
        # جعل governorate إجباري
        migrations.AlterField(
            model_name='district',
            name='governorate',
            field=models.ForeignKey(
                help_text='المحافظة التابع لها الحي',
                on_delete=django.db.models.deletion.PROTECT,
                related_name='districts',
                to='directory.governorate',
                verbose_name='المحافظة'
            ),
        ),
        
        # تحديثات أخرى
        migrations.AlterField(
            model_name='district',
            name='slug',
            field=models.SlugField(allow_unicode=True, blank=True, max_length=150, unique=True, verbose_name='الرابط'),
        ),
        
        migrations.AlterUniqueTogether(
            name='district',
            unique_together={('governorate', 'name')},
        ),
        
        migrations.AlterModelOptions(
            name='district',
            options={'verbose_name': 'حي', 'verbose_name_plural': 'الأحياء', 'ordering': ['governorate', 'name']},
        ),
    ]

"""
Django Signals للتحكم التلقائي في حالة المحلات والأحياء
"""

from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from .models import Governorate, District, Business


@receiver(pre_save, sender=Governorate)
def deactivate_governorate_children(sender, instance, **kwargs):
    """
    عند إلغاء تفعيل محافظة، يتم إلغاء تفعيل جميع الأحياء والمحلات التابعة لها
    عند تفعيل محافظة، يتم تفعيل الأحياء والمحلات تلقائياً
    """
    if instance.pk:
        try:
            old_instance = Governorate.objects.get(pk=instance.pk)
            
            # ❌ إلغاء التفعيل
            if old_instance.is_active and not instance.is_active:
                # إلغاء تفعيل جميع الأحياء
                districts = District.objects.filter(governorate=instance)
                district_count = districts.count()
                districts.update(is_active=False)
                
                # إلغاء تفعيل جميع المحلات في هذه الأحياء
                business_count = Business.objects.filter(district__governorate=instance).update(is_active=False)
                
                print(f"❌ تم إلغاء تفعيل المحافظة: {instance.name}")
                print(f"   └─ {district_count} حي")
                print(f"   └─ {business_count} محل")
            
            # ✅ التفعيل
            elif not old_instance.is_active and instance.is_active:
                # تفعيل جميع الأحياء
                districts = District.objects.filter(governorate=instance)
                district_count = districts.update(is_active=True)
                
                # تفعيل جميع المحلات
                business_count = Business.objects.filter(district__governorate=instance).update(is_active=True)
                
                print(f"✅ تم تفعيل المحافظة: {instance.name}")
                print(f"   └─ {district_count} حي")
                print(f"   └─ {business_count} محل")
                
        except Governorate.DoesNotExist:
            pass


@receiver(pre_save, sender=District)
def deactivate_district_children(sender, instance, **kwargs):
    """
    عند إلغاء تفعيل حي، يتم إلغاء تفعيل جميع المحلات التابعة له
    عند تفعيل حي، يتم تفعيل جميع المحلات تلقائياً
    """
    if instance.pk:
        try:
            old_instance = District.objects.get(pk=instance.pk)
            
            # ❌ إلغاء التفعيل
            if old_instance.is_active and not instance.is_active:
                # إلغاء تفعيل جميع المحلات
                business_count = Business.objects.filter(district=instance).update(is_active=False)
                
                print(f"❌ تم إلغاء تفعيل الحي: {instance.name}")
                print(f"   └─ {business_count} محل")
            
            # ✅ التفعيل
            elif not old_instance.is_active and instance.is_active:
                # التحقق من أن المحافظة الأم نشطة
                if not instance.governorate.is_active:
                    # منع التفعيل إذا كانت المحافظة معطلة
                    instance.is_active = False
                    print(f"❌ لا يمكن تفعيل الحي: {instance.name}")
                    print(f"   └─ السبب: المحافظة {instance.governorate.name} معطلة")
                else:
                    # تفعيل جميع المحلات
                    business_count = Business.objects.filter(district=instance).update(is_active=True)
                    
                    print(f"✅ تم تفعيل الحي: {instance.name}")
                    print(f"   └─ {business_count} محل")
                
        except District.DoesNotExist:
            pass


@receiver(pre_save, sender=Business)
def validate_business_activation(sender, instance, **kwargs):
    """
    التحقق من أن الحي والمحافظة نشطين قبل تفعيل المحل
    """
    # فقط للتحديثات اليدوية (ليس من خلال bulk_update)
    if instance.is_active and instance.pk:
        try:
            # التحقق من الحي
            if not instance.district.is_active:
                instance.is_active = False
                print(f"❌ لا يمكن تفعيل المحل: {instance.name}")
                print(f"   └─ السبب: الحي {instance.district.name} معطل")
            
            # التحقق من المحافظة
            elif not instance.district.governorate.is_active:
                instance.is_active = False
                print(f"❌ لا يمكن تفعيل المحل: {instance.name}")
                print(f"   └─ السبب: المحافظة {instance.district.governorate.name} معطلة")
        except:
            pass


@receiver(post_save, sender=Governorate)
def log_governorate_status_change(sender, instance, created, **kwargs):
    """
    تسجيل التغييرات في حالة المحافظة
    """
    if created:
        print(f"🆕 تم إنشاء محافظة جديدة: {instance.name}")
    else:
        status = "نشطة ✅" if instance.is_active else "معطلة ❌"
        print(f"📝 حالة المحافظة: {instance.name} - {status}")


@receiver(post_save, sender=District)
def log_district_status_change(sender, instance, created, **kwargs):
    """
    تسجيل التغييرات في حالة الحي
    """
    if created:
        print(f"🆕 تم إنشاء حي جديد: {instance.name} في {instance.governorate.name}")
    else:
        status = "نشط ✅" if instance.is_active else "معطل ❌"
        print(f"📝 حالة الحي: {instance.name} - {status}")


@receiver(post_save, sender=Business)
def log_business_status_change(sender, instance, created, **kwargs):
    """
    تسجيل التغييرات في حالة المحل
    """
    if created:
        print(f"🆕 تم إنشاء محل جديد: {instance.name}")
    # لا نسجل التحديثات لتجنب الازدحام في Console

# accounts/forms.py

from django import forms
from django.contrib.auth import get_user_model
from directory.models import Business, Category, District

User = get_user_model()


class BusinessForm(forms.ModelForm):
    """فورم إضافة/تعديل محل"""
    
    owner = forms.ModelChoiceField(
        queryset=User.objects.all(),
        required=False,
        label='المالك',
        widget=forms.Select(attrs={
            'class': 'form-select',
        }),
        help_text='اختياري - سيتم استخدام حسابك إذا تركته فارغاً'
    )
    
    class Meta:
        model = Business
        fields = [
            'owner', 'name', 'slug', 'category', 'district',
            'description', 'phone', 'email', 'whatsapp', 'website',
            'address', 'location_url', 'working_hours', 'logo',
            'is_active', 'is_verified', 'is_featured'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'اسم المحل أو الخدمة'
            }),
            'slug': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'الرابط المختصر (اتركه فارغاً للإنشاء التلقائي)'
            }),
            'category': forms.Select(attrs={
                'class': 'form-select'
            }),
            'district': forms.Select(attrs={
                'class': 'form-select'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'وصف المحل والخدمات المقدمة'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '01xxxxxxxxx'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'email@example.com (اختياري)'
            }),
            'whatsapp': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '01xxxxxxxxx (اختياري)'
            }),
            'website': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://example.com (اختياري)'
            }),
            'address': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'العنوان التفصيلي'
            }),
            'location_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'رابط خرائط جوجل (اختياري)'
            }),
            'working_hours': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'مثال: من 9 صباحاً إلى 10 مساءً'
            }),
            'logo': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'is_verified': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'is_featured': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
        labels = {
            'owner': 'المالك',
            'name': 'اسم المحل',
            'slug': 'الرابط المختصر',
            'category': 'الفئة',
            'district': 'المنطقة',
            'description': 'الوصف',
            'phone': 'رقم الهاتف',
            'email': 'البريد الإلكتروني',
            'whatsapp': 'واتساب',
            'website': 'الموقع الإلكتروني',
            'address': 'العنوان',
            'location_url': 'رابط الموقع',
            'working_hours': 'ساعات العمل',
            'logo': 'الشعار',
            'is_active': 'نشط',
            'is_verified': 'موثق',
            'is_featured': 'مميز',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # جعل بعض الحقول اختيارية
        self.fields['slug'].required = False
        self.fields['email'].required = False
        self.fields['whatsapp'].required = False
        self.fields['website'].required = False
        self.fields['location_url'].required = False
        self.fields['working_hours'].required = False
        self.fields['logo'].required = False

from django import forms
from .models import Business, Governorate, District, Category


class BusinessForm(forms.ModelForm):
    """Form لإضافة/تعديل المحلات مع اختيار المحافظة والحي"""
    
    governorate = forms.ModelChoiceField(
        queryset=Governorate.objects.filter(is_active=True).order_by('order', 'name'),
        required=True,
        label='المحافظة',
        widget=forms.Select(attrs={
            'class': 'form-select form-select-lg',
            'id': 'id_governorate',
            'onchange': 'loadDistricts(this.value)'
        })
    )
    
    district = forms.ModelChoiceField(
        queryset=District.objects.none(),  # فاضي في البداية
        required=True,
        label='الحي',
        widget=forms.Select(attrs={
            'class': 'form-select form-select-lg',
            'id': 'id_district',
            'disabled': 'disabled'
        })
    )
    
    class Meta:
        model = Business
        fields = [
            'name', 'category', 'governorate', 'district',
            'logo', 'phone', 'whatsapp', 'email', 'website',
            'address', 'location_url', 'latitude', 'longitude',
            'description', 'working_hours'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'اسم المحل'
            }),
            
            'logo': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'cover_image': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),    
            'category': forms.Select(attrs={
                'class': 'form-select form-select-lg'
            }),
            'logo': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': '01xxxxxxxxx',
                'dir': 'ltr'
            }),
            'whatsapp': forms.TextInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': '01xxxxxxxxx (اختياري)',
                'dir': 'ltr'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'email@example.com'
            }),
            'website': forms.URLInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'https://example.com'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'العنوان التفصيلي'
            }),
            'location_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'رابط Google Maps (اختياري)'
            }),
            'latitude': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': 'any',
                'placeholder': 'خط العرض'
            }),
            'longitude': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': 'any',
                'placeholder': 'خط الطول'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'وصف المحل والخدمات المقدمة'
            }),
            'working_hours': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'مثال: السبت-الخميس: 9 صباحاً - 10 مساءً'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # لو في instance موجود (تعديل)
        if self.instance and self.instance.pk:
            # تحديد المحافظة من الحي
            self.fields['governorate'].initial = self.instance.district.governorate
            
            # تحميل أحياء المحافظة
            self.fields['district'].queryset = District.objects.filter(
                governorate=self.instance.district.governorate,
                is_active=True
            ).order_by('name')
            
            # إزالة disabled
            self.fields['district'].widget.attrs.pop('disabled', None)
    
    def clean(self):
        cleaned_data = super().clean()
        governorate = cleaned_data.get('governorate')
        district = cleaned_data.get('district')
        
        # التأكد من أن الحي ينتمي للمحافظة
        if governorate and district:
            if district.governorate != governorate:
                raise forms.ValidationError({
                    'district': 'الحي المختار لا ينتمي للمحافظة المحددة'
                })
        
        return cleaned_data


class BusinessSearchForm(forms.Form):
    """Form للبحث والفلترة"""
    
    q = forms.CharField(
        required=False,
        label='البحث',
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'ابحث عن محل أو خدمة...',
        })
    )
    
    governorate = forms.ModelChoiceField(
        queryset=Governorate.objects.filter(is_active=True).order_by('order', 'name'),
        required=False,
        label='المحافظة',
        widget=forms.Select(attrs={
            'class': 'form-select form-select-lg',
            'id': 'search_governorate',
            'onchange': 'filterDistricts(this.value)'
        })
    )
    
    district = forms.ModelChoiceField(
        queryset=District.objects.filter(is_active=True).order_by('name'),
        required=False,
        label='الحي',
        widget=forms.Select(attrs={
            'class': 'form-select form-select-lg',
            'id': 'search_district'
        })
    )
    
    category = forms.ModelChoiceField(
        queryset=Category.objects.filter(is_active=True).order_by('order', 'name'),
        required=False,
        label='الفئة',
        widget=forms.Select(attrs={
            'class': 'form-select form-select-lg'
        })
    )

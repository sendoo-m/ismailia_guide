# 🗺️ دليل الإسماعيلية - Ismailia Guide

<div align="center">

![Django](https://img.shields.io/badge/Django-6.0-green?style=for-the-badge&logo=django)
![Python](https://img.shields.io/badge/Python-3.13-blue?style=for-the-badge&logo=python)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)

**أول وأشمل دليل إلكتروني للمحلات التجارية والخدمات في محافظة الإسماعيلية**

[المميزات](#-المميزات) • [التثبيت](#-التثبيت) • [الاستخدام](#-الاستخدام) • [المساهمة](#-المساهمة)

</div>

---

## ✨ المميزات

- 🔍 **بحث ذكي** - فلاتر متقدمة حسب الفئة والموقع
- 🗺️ **خرائط تفاعلية** - OpenStreetMap مجاناً
- ⭐ **نظام تقييمات** - تقييمات ومراجعات من المستخدمين
- 📊 **لوحة تحكل احترافية** - لأصحاب المحلات
- 💳 **4 خطط اشتراك** - من مجاني حتى VIP
- 📱 **Responsive Design** - يعمل على جميع الأجهزة
- 📁 **Import/Export** - CSV للمنتجات
- 🎨 **واجهة عربية** - RTL كامل
- 🚀 **SEO Optimized** - محسّن لمحركات البحث
- ✨ **Animations** - تأثيرات حركية سلسة

---

## 🚀 التثبيت

### المتطلبات

- Python 3.11+
- pip
- virtualenv (اختياري لكن مُوصى به)

### خطوات التثبيت

1. **استنساخ المشروع**
git clone https://github.com/yourusername/ismailia-guide.git
cd ismailia-guide


2. **إنشاء بيئة افتراضية**
python -m venv venv

Windows
venv\Scripts\activate

Linux/Mac
source venv/bin/activate


3. **تثبيت المتطلبات**
pip install -r requirements.txt


4. **إعداد ملف البيئة**
cp .env.example .env

عدّل الملف حسب حاجتك

5. **إعداد قاعدة البيانات**
python manage.py makemigrations
python manage.py migrate


6. **إضافة بيانات تجريبية (اختياري)**
python manage.py seed_data


7. **تشغيل السيرفر**
python manage.py runserver


افتح المتصفح على: `http://127.0.0.1:8000`

---

## 📖 الاستخدام

### للمستخدمين
- ابحث عن المحلات والخدمات
- اعرض التفاصيل والأسعار
- اقرأ التقييمات
- تواصل مع أصحاب المحلات

### لأصحاب المحلات
1. سجل حسابك من `/accounts/register/`
2. أضف محلك وتفاصيله
3. أضف منتجاتك وخدماتك
4. اختر خطة الاشتراك المناسبة
5. تابع الإحصائيات من لوحة التحكم

### للمطورين
تشغيل في وضع التطوير
python manage.py runserver

إنشاء superuser
python manage.py createsuperuser

جمع الملفات الثابتة
python manage.py collectstatic

---

## 🎯 خطط الاشتراك

| الخطة | السعر/سنة | المنتجات | صور | أسعار | توصيل | ظهور مميز |
|-------|-----------|----------|------|--------|-------|-----------|
| **مجاني** | 0 ج | 5 | ❌ | ❌ | ❌ | ❌ |
| **أساسي** | 500 ج | 50 | ✅ | ✅ | ❌ | ❌ |
| **مميز** | 1200 ج | 200 | ✅ | ✅ | ✅ | ✅ |
| **VIP** | 2500 ج | ∞ | ✅ | ✅ | ✅ | ✅ |

---

## 📂 هيكل المشروع

ismailia_guide/
├── config/ # إعدادات Django
├── directory/ # التطبيق الرئيسي
│ ├── models.py
│ ├── views.py
│ ├── urls.py
│ └── templates/
├── accounts/ # حسابات المستخدمين
├── subscriptions/ # نظام الاشتراكات
├── products/ # المنتجات
├── payments/ # المدفوعات
├── static/ # CSS, JS, Images
├── templates/ # قوالب HTML
├── media/ # ملفات المستخدمين
├── requirements.txt
├── .env.example
└── README.md

---

## 🛠️ التقنيات المستخدمة

### Backend
- Django 6.0
- Python 3.13
- SQLite (قابل للتطوير لـ PostgreSQL)

### Frontend
- Bootstrap 5 (RTL)
- JavaScript (Vanilla)
- Font Awesome 6
- Leaflet.js (Maps)

### Tools
- Git & GitHub
- VSCode
- Django Admin
- Python Decouple

---

## 🤝 المساهمة

المساهمات مرحب بها! 

1. Fork المشروع
2. أنشئ branch جديد (`git checkout -b feature/amazing-feature`)
3. Commit تغييراتك (`git commit -m 'Add amazing feature'`)
4. Push للـ branch (`git push origin feature/amazing-feature`)
5. افتح Pull Request

---

## 📄 الترخيص

هذا المشروع مرخص تحت MIT License - راجع ملف [LICENSE](LICENSE) للتفاصيل.

---

## 📞 التواصل

- **الموقع:** [ismailia-guide.com](https://ismailia-guide.com)
- **البريد:** info@ismailia-guide.com
- **الهاتف:** 01234567890
- **واتساب:** [wa.me/201234567890](https://wa.me/201234567890)

---

## 🙏 شكر وتقدير

- [Django](https://www.djangoproject.com/) - Web Framework
- [Bootstrap](https://getbootstrap.com/) - CSS Framework
- [Font Awesome](https://fontawesome.com/) - Icons
- [OpenStreetMap](https://www.openstreetmap.org/) - Maps
- [Leaflet](https://leafletjs.com/) - Map Library

---

<div align="center">

**صُنع بـ ❤️ في الإسماعيلية، مصر 🇪🇬**

⭐ إذا أعجبك المشروع، لا تنسى النجمة!

</div>

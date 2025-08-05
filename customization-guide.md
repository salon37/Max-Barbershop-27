# دليل التخصيص المفصل - قالب صالون مينيسا

## 🎨 تخصيص الألوان

### الألوان الأساسية
```css
/* استبدل هذه القيم في ملف CSS */
:root {
  --primary-color: #e74c3c;      /* اللون الأحمر الأساسي */
  --secondary-color: #2c3e50;    /* اللون الأزرق الداكن */
  --accent-color: #c0392b;       /* لون التأثيرات */
  --text-color: #333;            /* لون النص الأساسي */
  --light-bg: #f8f9fa;          /* خلفية فاتحة */
  --white: #ffffff;              /* اللون الأبيض */
  --dark-footer: #1a252f;       /* لون التذييل الداكن */
}
```

### تغيير الألوان في القالب
1. **اللون الأساسي** (الأحمر): ابحث عن `#e74c3c` واستبدله
2. **اللون الثانوي** (الأزرق): ابحث عن `#2c3e50` واستبدله
3. **لون التأثيرات**: ابحث عن `#c0392b` واستبدله

## 📝 تخصيص النصوص

### العناوين الرئيسية
```html
<!-- عنوان الصالون -->
<h1>مرحباً بكم في صالون مينيسا</h1>

<!-- الوصف -->
<p>خبرة احترافية في عالم الجمال والأناقة منذ سنوات</p>

<!-- زر الحث على العمل -->
<a href='#contact' class='cta-button'>احجز موعدك الآن</a>
```

### قسم "من نحن"
```html
<h3>صالون مينيسا للجمال</h3>
<p>نحن في صالون مينيسا نؤمن بأن الجمال هو انعكاس للثقة بالنفس...</p>
```

## 🖼️ تخصيص الصور

### صورة الخلفية الرئيسية
```css
.hero-section {
  background: linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.5)), 
              url('رابط_الصورة_الجديدة');
}
```

### صور الفريق
```html
<!-- استبدل روابط الصور -->
<img src='رابط_صورة_مينيسا' alt='مينيسا - المديرة العامة'/>
<img src='رابط_صورة_سارة' alt='سارة - خبيرة تجميل'/>
<img src='رابط_صورة_نور' alt='نور - مصففة شعر'/>
<img src='رابط_صورة_ليلى' alt='ليلى - خبيرة أظافر'/>
```

### صورة "من نحن"
```html
<img src='رابط_صورة_الصالون' alt='صالون مينيسا'/>
```

## 📞 تخصيص معلومات الاتصال

### الهاتف والبريد الإلكتروني
```html
<div class='contact-item'>
  <i class='fas fa-phone'></i>
  <span>رقم_الهاتف_الجديد</span>
</div>
<div class='contact-item'>
  <i class='fas fa-envelope'></i>
  <span>البريد_الإلكتروني_الجديد</span>
</div>
```

### العنوان
```html
<div class='contact-item'>
  <i class='fas fa-map-marker-alt'></i>
  <span>العنوان_الجديد</span>
</div>
```

### الموقع الإلكتروني
```html
<div class='contact-item'>
  <i class='fas fa-globe'></i>
  <span>الموقع_الإلكتروني_الجديد</span>
</div>
```

## 🕐 تخصيص ساعات العمل

```html
<div class='hours-item'>
  <span>اليوم</span>
  <span>الساعات</span>
</div>
```

مثال:
```html
<div class='hours-item'>
  <span>السبت - الخميس</span>
  <span>09:00 - 20:00</span>
</div>
<div class='hours-item'>
  <span>الجمعة</span>
  <span>14:00 - 20:00</span>
</div>
```

## 🛠️ تخصيص الخدمات

### إضافة خدمة جديدة
```html
<div class='service-card'>
  <div class='service-icon'>
    <i class='fas fa-أيقونة_الخدمة'></i>
  </div>
  <h3>اسم الخدمة</h3>
  <p>وصف الخدمة</p>
</div>
```

### أيقونات الخدمات المتاحة
- `fas fa-cut` - قص الشعر
- `fas fa-palette` - الصبغ
- `fas fa-spa` - العلاجات
- `fas fa-crown` - التسريحات
- `fas fa-hand-sparkles` - الأظافر
- `fas fa-eye` - الحواجب
- `fas fa-brush` - المكياج
- `fas fa-heart` - العناية بالبشرة

## 👥 تخصيص فريق العمل

### إضافة عضو جديد
```html
<div class='team-member'>
  <img src='رابط_الصورة' alt='اسم_العضو'/>
  <h3>اسم العضو</h3>
  <p>المنصب والتخصص</p>
</div>
```

### حذف عضو من الفريق
احذف الكود الكامل لعضو الفريق من قسم `.team-grid`

## 🌐 تخصيص الروابط الاجتماعية

```html
<div class='social-links'>
  <a href='رابط_فيسبوك'><i class='fab fa-facebook'></i></a>
  <a href='رابط_انستغرام'><i class='fab fa-instagram'></i></a>
  <a href='رابط_تويتر'><i class='fab fa-twitter'></i></a>
  <a href='رابط_واتساب'><i class='fab fa-whatsapp'></i></a>
  <a href='رابط_تيك_توك'><i class='fab fa-tiktok'></i></a>
  <a href='رابط_يوتيوب'><i class='fab fa-youtube'></i></a>
</div>
```

## 📱 تخصيص التصميم المتجاوب

### نقاط التوقف (Breakpoints)
```css
/* الهواتف الصغيرة */
@media (max-width: 480px) {
  /* التخصيصات */
}

/* الهواتف الكبيرة */
@media (max-width: 768px) {
  /* التخصيصات */
}

/* الأجهزة اللوحية */
@media (max-width: 1024px) {
  /* التخصيصات */
}

/* أجهزة الكمبيوتر */
@media (min-width: 1200px) {
  /* التخصيصات */
}
```

## 🎭 تخصيص الخطوط

### تغيير الخط الأساسي
```css
body {
  font-family: 'خط_جديد', sans-serif;
}
```

### تغيير خط العناوين
```css
.section-title,
.hero-content h1,
.logo {
  font-family: 'خط_العناوين_الجديد', serif;
}
```

### خطوط Google المقترحة للعربية
- `'Amiri', serif` - خط أميري
- `'Cairo', sans-serif` - خط القاهرة
- `'Tajawal', sans-serif` - خط تجوال
- `'Almarai', sans-serif` - خط المرعي

## 🎨 تخصيص التأثيرات البصرية

### تأثيرات الحركة
```css
/* تأثير التحويم على البطاقات */
.service-card:hover {
  transform: translateY(-10px); /* غير القيمة */
  box-shadow: 0 10px 40px rgba(0,0,0,0.2); /* غير الظل */
}
```

### تأثيرات الانتقال
```css
/* سرعة الانتقالات */
.nav-menu a,
.cta-button,
.service-card {
  transition: all 0.5s ease; /* غير المدة */
}
```

## 🔧 نصائح التخصيص المتقدم

### 1. استخدام متغيرات CSS
```css
:root {
  --border-radius: 15px;
  --box-shadow: 0 5px 20px rgba(0,0,0,0.1);
  --transition: all 0.3s ease;
}
```

### 2. تخصيص الأزرار
```css
.custom-button {
  background: linear-gradient(45deg, #color1, #color2);
  border: none;
  padding: 12px 24px;
  border-radius: var(--border-radius);
}
```

### 3. إضافة قسم جديد
```html
<section class='new-section'>
  <div class='container'>
    <h2 class='section-title'>عنوان القسم</h2>
    <div class='section-content'>
      <!-- محتوى القسم -->
    </div>
  </div>
</section>
```

## ⚠️ تحذيرات مهمة

1. **احتفظ بنسخة احتياطية** قبل أي تعديل
2. **اختبر التغييرات** على أجهزة مختلفة
3. **تأكد من صحة الكود** قبل الحفظ
4. **لا تحذف** العناصر الأساسية لبلوجر
5. **استخدم أدوات المطور** في المتصفح للاختبار

## 📞 الدعم والمساعدة

إذا واجهت صعوبة في التخصيص:
1. راجع هذا الدليل مرة أخرى
2. تأكد من صحة الكود المستخدم
3. اختبر التغييرات تدريجياً
4. استخدم أدوات المطور في المتصفح
# مكتبة استخراج بيانات كاميرات المراقبة

مكتبة Python لاستخراج بيانات منتجات كاميرات المراقبة من مواقع الشركات المصنعة بشكل آلي.

## الميزات الرئيسية

- استخراج بيانات منتجات كاميرات المراقبة من مواقع الشركات المصنعة.
- دعم لشركتي Hikvision و Dahua مع إمكانية إضافة دعم لشركات أخرى مستقبلاً.
- تصدير البيانات المستخرجة بتنسيقات متعددة (JSON, CSV, Excel).
- معالجة متقدمة للأخطاء والاسترداد التلقائي.
- هيكل منظم وقابل للتوسعة.

## متطلبات التثبيت

```bash
pip install requests beautifulsoup4 lxml pandas openpyxl
```

## التثبيت

### من مصدر المكتبة

```bash
# استنساخ المستودع
git clone https://github.com/username/security_cameras_scraper.git
cd security_cameras_scraper

# تثبيت المكتبة في وضع التطوير
pip install -e .
```

## طريقة الاستخدام

### استخراج بيانات منتج واحد

```python
from security_cameras_scraper import CameraScraper

# إنشاء كائن CameraScraper
scraper = CameraScraper()

# استخراج بيانات منتج من رابط
url = "https://www.hikvision.com/en/products/Turbo-HD-Products/DVR/AcuSense-Series/iDS-7208HUHI-M1-S/"
data = scraper.scrape(url)

# تصدير البيانات إلى ملف JSON
scraper.export_to_json(data, "camera_specs.json")

# تصدير البيانات إلى ملف CSV
scraper.export_to_csv(data, "camera_specs.csv")

# تصدير البيانات إلى ملف Excel
scraper.export_to_excel(data, "camera_specs.xlsx")
```

### استخراج بيانات عدة منتجات

```python
from security_cameras_scraper import CameraScraper

# إنشاء كائن CameraScraper
scraper = CameraScraper()

# قائمة روابط المنتجات
urls = [
    "https://www.hikvision.com/en/products/Turbo-HD-Products/DVR/AcuSense-Series/iDS-7208HUHI-M1-S/",
    "https://www.dahuasecurity.com/es/products/All-Products/HDCVI-Cameras/Lite-Series/1080P/1080-P/HAC-HFW1200TH-I8-A=S6"
]

# استخراج بيانات جميع المنتجات
results = scraper.scrape_multiple(urls)

# تصدير نتيجة كل منتج إلى ملف منفصل
for url, data in results.items():
    # استخراج اسم الملف من نهاية الرابط
    filename = url.split('/')[-2] if url.endswith('/') else url.split('/')[-1]
    
    # تصدير البيانات إلى ملف JSON
    scraper.export_to_json(data, f"{filename}.json")
    
    # يمكن أيضًا تصدير البيانات إلى ملفات CSV أو Excel
    scraper.export_to_csv(data, f"{filename}.csv")
    scraper.export_to_excel(data, f"{filename}.xlsx")

# تصدير جميع البيانات إلى ملف Excel واحد متعدد الأوراق
from security_cameras_scraper.export.excel_exporter import export_multi_sheet_excel
export_multi_sheet_excel(results, "all_cameras.xlsx")
```

### استخدام المستخرجات بشكل مباشر

```python
from security_cameras_scraper.scrapers.hikvision_scraper import HikvisionScraper
from security_cameras_scraper.utils.http_utils import fetch_page

# استرجاع محتوى HTML
url = "https://www.hikvision.com/en/products/Turbo-HD-Products/DVR/AcuSense-Series/iDS-7208HUHI-M1-S/"
html_content = fetch_page(url)

# استخدام مستخرج Hikvision
hikvision_scraper = HikvisionScraper()
data = hikvision_scraper.extract(html_content, url)

print(data)
```

### إضافة دعم لشركة جديدة

```python
from security_cameras_scraper import CameraScraper
from bs4 import BeautifulSoup

class CustomScraper:
    """مستخرج مخصص لشركة جديدة."""
    
    def __init__(self):
        """تهيئة المستخرج المخصص."""
        self.name = "Custom"
    
    def extract(self, html_content, url):
        """استخراج البيانات من HTML."""
        soup = BeautifulSoup(html_content, 'lxml')
        data = {"General information": {}}
        
        # هنا يمكنك إضافة منطق استخراج البيانات الخاص بالشركة الجديدة
        # ...
        
        return data

# إنشاء كائن CameraScraper
scraper = CameraScraper()

# إضافة المستخرج المخصص
scraper.add_manufacturer_scraper("custom", CustomScraper())

# استخدام المستخرج المخصص
url = "https://www.custom-manufacturer.com/products/camera123"
data = scraper.scrape(url)
```

## هيكل المشروع

```
security_cameras_scraper/
│
├── __init__.py                 # تصدير الواجهات الرئيسية
├── scraper.py                  # الكلاس الرئيسي للمكتبة
├── scrapers/
│   ├── __init__.py
│   ├── hikvision_scraper.py    # محدد لـ Hikvision
│   └── dahua_scraper.py        # محدد لـ Dahua
├── utils/
│   ├── __init__.py
│   ├── http_utils.py           # أدوات طلبات HTTP
│   ├── html_utils.py           # أدوات تحليل HTML
│   └── data_utils.py           # أدوات معالجة البيانات
└── export/
    ├── __init__.py
    ├── json_exporter.py        # تصدير إلى JSON
    ├── csv_exporter.py         # تصدير إلى CSV
    └── excel_exporter.py       # تصدير إلى Excel
```

## الخطوات التالية - المرحلة الثانية (واجهة الويب)

الخطة المستقبلية تشمل تطوير واجهة ويب تستخدم هذه المكتبة وتوفر المميزات التالية:

- إمكانية إدخال رابط منتج لاستخراج بياناته
- عرض النتائج بتنسيق منظم
- إمكانية تصدير البيانات بعدة صيغ
- ميزة مقارنة المنتجات
- إمكانية استخراج بيانات مجموعة من الروابط دفعة واحدة

## المساهمة

نرحب بالمساهمات! يرجى إرسال طلبات السحب أو فتح مشكلة لتقديم اقتراحات أو تقارير عن أخطاء.

## الترخيص

تم ترخيص هذا المشروع بموجب رخصة MIT.
```
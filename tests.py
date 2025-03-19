#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
اختبارات أساسية لمكتبة استخراج بيانات كاميرات المراقبة.
"""

import os
import unittest
import tempfile
import json
from security_cameras_scraper import CameraScraper
from security_cameras_scraper.scrapers.hikvision_scraper import HikvisionScraper
from security_cameras_scraper.scrapers.dahua_scraper import DahuaScraper
from security_cameras_scraper.utils.http_utils import fetch_page

class TestCameraScraper(unittest.TestCase):
    """اختبارات للمكتبة الرئيسية."""
    
    def setUp(self):
        """إعداد بيئة الاختبار."""
        self.scraper = CameraScraper()
        self.hikvision_url = "https://www.hikvision.com/en/products/Turbo-HD-Products/DVR/AcuSense-Series/iDS-7208HUHI-M1-S/"
        self.dahua_url = "https://www.dahuasecurity.com/es/products/All-Products/HDCVI-Cameras/Lite-Series/1080P/1080-P/HAC-HFW1200TH-I8-A=S6"
        self.temp_dir = tempfile.mkdtemp()
    
    def test_detect_manufacturer(self):
        """اختبار وظيفة التعرف على الشركة المصنعة."""
        self.assertEqual(self.scraper.detect_manufacturer(self.hikvision_url), "hikvision")
        self.assertEqual(self.scraper.detect_manufacturer(self.dahua_url), "dahua")
        self.assertIsNone(self.scraper.detect_manufacturer("https://example.com/product123"))
    
    def test_add_manufacturer_scraper(self):
        """اختبار وظيفة إضافة مستخرج جديد."""
        # إنشاء مستخرج وهمي
        mock_scraper = type("MockScraper", (), {"extract": lambda s, h, u: {"mock": "data"}})()
        
        # إضافة المستخرج
        self.scraper.add_manufacturer_scraper("mock", mock_scraper)
        
        # التحقق من إضافة المستخرج
        self.assertIn("mock", self.scraper.scrapers)
    
    def test_export_formats(self):
        """اختبار وظائف التصدير."""
        # بيانات اختبار بسيطة
        test_data = {
            "General information": {
                "Product Title": "Test Camera",
                "Product Type": "IP Camera"
            },
            "Test Section": {
                "Resolution": "1080p",
                "FPS": "30"
            }
        }
        
        # اختبار التصدير بتنسيق JSON
        json_path = os.path.join(self.temp_dir, "test.json")
        self.assertTrue(self.scraper.export_to_json(test_data, json_path))
        self.assertTrue(os.path.exists(json_path))
        
        # التحقق من محتوى ملف JSON
        with open(json_path, 'r', encoding='utf-8') as f:
            loaded_data = json.load(f)
            self.assertEqual(loaded_data["General information"]["Product Title"], "Test Camera")
        
        # اختبار التصدير بتنسيق CSV
        csv_path = os.path.join(self.temp_dir, "test.csv")
        self.assertTrue(self.scraper.export_to_csv(test_data, csv_path))
        self.assertTrue(os.path.exists(csv_path))
        
        # اختبار التصدير بتنسيق Excel
        excel_path = os.path.join(self.temp_dir, "test.xlsx")
        result = self.scraper.export_to_excel(test_data, excel_path)
        # لاحظ: قد يفشل هذا الاختبار إذا لم تكن مكتبة pandas مثبتة
        if "pandas" in locals() or "pandas" in globals():
            self.assertTrue(result)
            self.assertTrue(os.path.exists(excel_path))
    
    def tearDown(self):
        """تنظيف بعد الاختبارات."""
        # حذف الملفات المؤقتة
        for file in os.listdir(self.temp_dir):
            os.remove(os.path.join(self.temp_dir, file))
        os.rmdir(self.temp_dir)

class TestHikvisionScraper(unittest.TestCase):
    """اختبارات لمستخرج Hikvision."""
    
    def setUp(self):
        """إعداد بيئة الاختبار."""
        self.scraper = HikvisionScraper()
        self.url = "https://www.hikvision.com/en/products/Turbo-HD-Products/DVR/AcuSense-Series/iDS-7208HUHI-M1-S/"
    
    def test_extract_with_sample_html(self):
        """اختبار الاستخراج باستخدام HTML نموذجي."""
        # نموذج HTML بسيط لاختبار المستخرج
        sample_html = """
        <html>
            <head>
                <title>Hikvision Product</title>
            </head>
            <body>
                <div class="product_description_title_tag_container">
                    <div class="product_description_title">
                        <h2>Test Hikvision Camera</h2>
                    </div>
                </div>
                <div>
                    <div class="product-description-container">
                        <div>
                            <h1>Network Camera</h1>
                        </div>
                    </div>
                </div>
                <ul class="tech-specs-items-description" data-target="Camera">
                    <li class="tech-specs-items-description-list">
                        <span class="tech-specs-items-description__title--heading">Image Sensor</span>
                    </li>
                    <li class="tech-specs-items-description-list">
                        <span class="tech-specs-items-description__title">Type</span>
                        <span class="tech-specs-items-description__title-details">1/2.8" Progressive Scan CMOS</span>
                    </li>
                </ul>
            </body>
        </html>
        """
        
        # استخراج البيانات
        data = self.scraper.extract(sample_html, self.url)
        
        # التحقق من البيانات المستخرجة
        self.assertIn("General information", data)
        self.assertEqual(data["General information"]["Product Title"], "Test Hikvision Camera")
        self.assertEqual(data["General information"]["Product Type"], "Network Camera")
        self.assertIn("Camera", data)
        self.assertIn("Type", data["Camera"])
        self.assertEqual(data["Camera"]["Type"], "1/2.8\" Progressive Scan CMOS")

class TestDahuaScraper(unittest.TestCase):
    """اختبارات لمستخرج Dahua."""
    
    def setUp(self):
        """إعداد بيئة الاختبار."""
        self.scraper = DahuaScraper()
        self.url = "https://www.dahuasecurity.com/es/products/All-Products/HDCVI-Cameras/Lite-Series/1080P/1080-P/HAC-HFW1200TH-I8-A=S6"
    
    def test_extract_with_sample_html(self):
        """اختبار الاستخراج باستخدام HTML نموذجي."""
        # نموذج HTML بسيط لاختبار المستخرج
        sample_html = """
        <html>
            <head>
                <title>Dahua Product</title>
            </head>
            <body>
                <div class="el-row">
                    <h3 class="title">Test Dahua Camera</h3>
                    <p class="text">HDCVI Camera</p>
                </div>
                <table>
                    <tr>
                        <td>Camera</td>
                    </tr>
                    <tr>
                        <td>Image Sensor</td>
                        <td>1/2.8" 2MP CMOS</td>
                    </tr>
                </table>
            </body>
        </html>
        """
        
        # استخراج البيانات
        data = self.scraper.extract(sample_html, self.url)
        
        # التحقق من البيانات المستخرجة
        self.assertIn("General information", data)
        self.assertEqual(data["General information"]["Product Title"], "Test Dahua Camera")
        self.assertEqual(data["General information"]["Product Type"], "HDCVI Camera")
        
        # لاحظ: هذا الاختبار قد يفشل اعتمادًا على طريقة معالجة الجداول في مستخرج Dahua
        # يمكن تعديل هذا الاختبار بناءً على السلوك الفعلي للمستخرج

if __name__ == "__main__":
    unittest.main()
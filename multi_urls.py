#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
مثال على استخراج بيانات من عدة روابط.
"""

from security_cameras_scraper import CameraScraper
import os
import time
import json
from datetime import datetime

def main():
    """الدالة الرئيسية."""
    
    # إنشاء كائن CameraScraper
    print("إنشاء مستخرج الكاميرا...")
    scraper = CameraScraper()
    
    # قائمة روابط المنتجات
    urls = [
        "https://www.hikvision.com/en/products/Turbo-HD-Products/DVR/AcuSense-Series/iDS-7208HUHI-M1-S/",
        "https://www.dahuasecurity.com/es/products/All-Products/HDCVI-Cameras/Lite-Series/1080P/1080-P/HAC-HFW1200TH-I8-A=S6"
        # يمكنك إضافة المزيد من الروابط هنا
    ]
    
    # إنشاء مجلد للإخراج مع الطابع الزمني
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = f"output_{timestamp}"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"\nتم إنشاء مجلد الإخراج: {output_dir}")
    
    # استخراج البيانات من كل رابط
    print(f"\nبدء استخراج البيانات من {len(urls)} رابط...")
    
    all_data = {}
    
    for i, url in enumerate(urls, 1):
        print(f"\n[{i}/{len(urls)}] جاري استخراج البيانات من: {url}")
        
        try:
            # استخراج البيانات
            start_time = time.time()
            data = scraper.scrape(url)
            elapsed_time = time.time() - start_time
            
            # حفظ البيانات في القاموس الكلي
            all_data[url] = data
            
            # طباعة ملخص البيانات المستخرجة
            if "General information" in data:
                print(f"✓ عنوان المنتج: {data['General information'].get('Product Title', 'غير متوفر')}")
                print(f"✓ نوع المنتج: {data['General information'].get('Product Type', 'غير متوفر')}")
            
            # استخراج اسم الملف من نهاية الرابط
            filename = url.split('/')[-2] if url.endswith('/') else url.split('/')[-1]
            filename = filename.replace('=', '_')  # استبدال الأحرف غير الصالحة لاسم الملف
            
            # تصدير البيانات بتنسيق JSON
            json_path = os.path.join(output_dir, f"{filename}.json")
            if scraper.export_to_json(data, json_path):
                print(f"✓ تم تصدير البيانات إلى JSON: {json_path}")
            
            # تصدير البيانات بتنسيق CSV
            csv_path = os.path.join(output_dir, f"{filename}.csv")
            if scraper.export_to_csv(data, csv_path):
                print(f"✓ تم تصدير البيانات إلى CSV: {csv_path}")
            
            # تصدير البيانات بتنسيق Excel
            excel_path = os.path.join(output_dir, f"{filename}.xlsx")
            if scraper.export_to_excel(data, excel_path):
                print(f"✓ تم تصدير البيانات إلى Excel: {excel_path}")
            
            print(f"✓ اكتمل الاستخراج في {elapsed_time:.2f} ثانية")
            
        except Exception as e:
            print(f"✗ خطأ في استخراج البيانات من {url}: {str(e)}")
    
    # تصدير جميع البيانات إلى ملف واحد
    all_data_path = os.path.join(output_dir, "all_cameras.json")
    with open(all_data_path, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    print(f"\n✓ تم تصدير جميع البيانات إلى ملف واحد: {all_data_path}")
    
    # تصدير جميع البيانات إلى ملف Excel واحد متعدد الأوراق
    from security_cameras_scraper.export.excel_exporter import export_multi_sheet_excel
    excel_all_path = os.path.join(output_dir, "all_cameras.xlsx")
    if export_multi_sheet_excel(all_data, excel_all_path):
        print(f"✓ تم تصدير جميع البيانات إلى ملف Excel متعدد الأوراق: {excel_all_path}")
    
    print("\nتم الانتهاء من استخراج وتصدير البيانات بنجاح!")
    print(f"يمكنك العثور على ملفات البيانات في مجلد: {os.path.abspath(output_dir)}")

if __name__ == "__main__":
    main()
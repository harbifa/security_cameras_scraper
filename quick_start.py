#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
ملف بدء سريع لاستخدام مكتبة استخراج بيانات كاميرات المراقبة.
"""

from security_cameras_scraper import CameraScraper
import os
import json

def main():
    """الدالة الرئيسية."""
    
    # إنشاء كائن CameraScraper
    print("إنشاء مستخرج الكاميرا...")
    scraper = CameraScraper()
    
    # رابط المنتج الذي تريد استخراج بياناته
    url = "https://www.hikvision.com/en/products/Turbo-HD-Products/DVR/AcuSense-Series/iDS-7208HUHI-M1-S/"
    
    # استخراج البيانات
    print(f"جاري استخراج البيانات من: {url}")
    data = scraper.scrape(url)
    
    # طباعة ملخص البيانات المستخرجة
    print("\nملخص البيانات المستخرجة:")
    if "General information" in data:
        print(f"عنوان المنتج: {data['General information'].get('Product Title', 'غير متوفر')}")
        print(f"نوع المنتج: {data['General information'].get('Product Type', 'غير متوفر')}")
    
    # عرض أقسام البيانات
    print("\nأقسام البيانات المستخرجة:")
    for section_name in data.keys():
        if section_name != "General information":
            item_count = len(data[section_name])
            print(f"- {section_name}: {item_count} عنصر")
    
    # إنشاء مجلد للإخراج
    output_dir = "output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"\nتم إنشاء مجلد الإخراج: {output_dir}")
    
    # تصدير البيانات بتنسيق JSON
    json_path = os.path.join(output_dir, "camera_specs.json")
    print(f"جاري تصدير البيانات إلى JSON: {json_path}")
    if scraper.export_to_json(data, json_path):
        print("✓ تم التصدير بنجاح")
    
    # تصدير البيانات بتنسيق CSV
    csv_path = os.path.join(output_dir, "camera_specs.csv")
    print(f"جاري تصدير البيانات إلى CSV: {csv_path}")
    if scraper.export_to_csv(data, csv_path):
        print("✓ تم التصدير بنجاح")
    
    # تصدير البيانات بتنسيق Excel
    excel_path = os.path.join(output_dir, "camera_specs.xlsx")
    print(f"جاري تصدير البيانات إلى Excel: {excel_path}")
    if scraper.export_to_excel(data, excel_path):
        print("✓ تم التصدير بنجاح")
    
    print("\nتم الانتهاء من استخراج وتصدير البيانات بنجاح!")
    print(f"يمكنك العثور على ملفات البيانات في مجلد: {os.path.abspath(output_dir)}")

if __name__ == "__main__":
    main()
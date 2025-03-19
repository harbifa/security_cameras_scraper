#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
مثال على استخدام مكتبة استخراج بيانات كاميرات المراقبة.
"""

import os
import argparse
import logging
from security_cameras_scraper import CameraScraper

# إعداد تسجيل الأحداث
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def setup_argparse():
    """إعداد معالج الأوامر."""
    parser = argparse.ArgumentParser(description='استخراج بيانات منتجات كاميرات المراقبة')
    
    parser.add_argument('--url', type=str, help='رابط منتج لاستخراج بياناته')
    parser.add_argument('--file', type=str, help='ملف نصي يحتوي على قائمة روابط منتجات (رابط واحد في كل سطر)')
    parser.add_argument('--output', type=str, default='output', help='مجلد الإخراج (الافتراضي: output)')
    parser.add_argument('--format', type=str, choices=['json', 'csv', 'excel', 'all'], default='json',
                       help='تنسيق الإخراج (الافتراضي: json)')
    
    return parser.parse_args()

def ensure_output_dir(output_dir):
    """التأكد من وجود مجلد الإخراج."""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        logger.info(f"تم إنشاء مجلد الإخراج: {output_dir}")

def process_url(url, scraper, output_dir, output_format):
    """معالجة رابط منتج واحد."""
    logger.info(f"جاري استخراج بيانات المنتج من: {url}")
    
    # استخراج البيانات
    data = scraper.scrape(url)
    
    if not data:
        logger.warning(f"لم يتم استخراج أي بيانات من: {url}")
        return
    
    # استخراج اسم ملف الإخراج من الرابط
    filename = url.split('/')[-2] if url.endswith('/') else url.split('/')[-1]
    filename = filename.replace('=', '_')  # استبدال الأحرف غير الصالحة لاسم الملف
    
    # تصدير البيانات بالتنسيق المطلوب
    if output_format in ['json', 'all']:
        output_file = os.path.join(output_dir, f"{filename}.json")
        if scraper.export_to_json(data, output_file):
            logger.info(f"تم تصدير البيانات إلى: {output_file}")
    
    if output_format in ['csv', 'all']:
        output_file = os.path.join(output_dir, f"{filename}.csv")
        if scraper.export_to_csv(data, output_file):
            logger.info(f"تم تصدير البيانات إلى: {output_file}")
    
    if output_format in ['excel', 'all']:
        output_file = os.path.join(output_dir, f"{filename}.xlsx")
        if scraper.export_to_excel(data, output_file):
            logger.info(f"تم تصدير البيانات إلى: {output_file}")

def process_file(file_path, scraper, output_dir, output_format):
    """معالجة ملف يحتوي على قائمة روابط."""
    if not os.path.exists(file_path):
        logger.error(f"الملف غير موجود: {file_path}")
        return
    
    # قراءة الروابط من الملف
    with open(file_path, 'r', encoding='utf-8') as f:
        urls = [line.strip() for line in f if line.strip()]
    
    if not urls:
        logger.warning(f"لا توجد روابط في الملف: {file_path}")
        return
    
    logger.info(f"تم العثور على {len(urls)} رابط في الملف")
    
    # استخراج البيانات من جميع الروابط
    results = scraper.scrape_multiple(urls)
    
    # تصدير نتيجة كل منتج إلى ملف منفصل
    for url, data in results.items():
        if 'error' in data:
            logger.warning(f"خطأ في استخراج البيانات من {url}: {data['error']}")
            continue
        
        # استخراج اسم ملف الإخراج من الرابط
        filename = url.split('/')[-2] if url.endswith('/') else url.split('/')[-1]
        filename = filename.replace('=', '_')  # استبدال الأحرف غير الصالحة لاسم الملف
        
        # تصدير البيانات بالتنسيق المطلوب
        if output_format in ['json', 'all']:
            output_file = os.path.join(output_dir, f"{filename}.json")
            if scraper.export_to_json(data, output_file):
                logger.info(f"تم تصدير البيانات إلى: {output_file}")
        
        if output_format in ['csv', 'all']:
            output_file = os.path.join(output_dir, f"{filename}.csv")
            if scraper.export_to_csv(data, output_file):
                logger.info(f"تم تصدير البيانات إلى: {output_file}")
        
        if output_format in ['excel', 'all']:
            output_file = os.path.join(output_dir, f"{filename}.xlsx")
            if scraper.export_to_excel(data, output_file):
                logger.info(f"تم تصدير البيانات إلى: {output_file}")
    
    # تصدير جميع البيانات إلى ملف واحد متعدد الأوراق
    if output_format in ['excel', 'all']:
        from security_cameras_scraper.export.excel_exporter import export_multi_sheet_excel
        output_file = os.path.join(output_dir, "all_cameras.xlsx")
        if export_multi_sheet_excel(results, output_file):
            logger.info(f"تم تصدير جميع البيانات إلى: {output_file}")

def main():
    """الدالة الرئيسية."""
    args = setup_argparse()
    
    # التأكد من وجود مجلد الإخراج
    ensure_output_dir(args.output)
    
    # إنشاء كائن CameraScraper
    scraper = CameraScraper()
    
    # معالجة الرابط أو الملف
    if args.url:
        process_url(args.url, scraper, args.output, args.format)
    elif args.file:
        process_file(args.file, scraper, args.output, args.format)
    else:
        logger.error("يرجى تحديد رابط منتج (--url) أو ملف يحتوي على روابط (--file)")

if __name__ == "__main__":
    main()
# الملف: security_cameras_scraper/export/json_exporter.py

"""
أداة لتصدير البيانات المستخرجة بتنسيق JSON.
"""

import os
import json
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

def export_json(data: Dict[str, Any], 
               file_path: str, 
               indent: int = 4, 
               ensure_ascii: bool = False) -> bool:
    """
    تصدير البيانات إلى ملف JSON.
    
    المعاملات:
        data (Dict[str, Any]): البيانات المراد تصديرها.
        file_path (str): مسار الملف للتصدير.
        indent (int): عدد المسافات للتنسيق.
        ensure_ascii (bool): ما إذا كان سيتم ضمان استخدام ASCII فقط.
        
    العوائد:
        bool: True إذا نجحت عملية التصدير، False في حالة الفشل.
    """
    if not data:
        logger.warning("لا توجد بيانات للتصدير")
        return False
    
    try:
        # التأكد من وجود المجلد الأب
        parent_dir = os.path.dirname(file_path)
        if parent_dir and not os.path.exists(parent_dir):
            os.makedirs(parent_dir)
        
        # تصدير البيانات إلى ملف JSON
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=ensure_ascii, indent=indent)
        
        logger.info(f"تم تصدير البيانات بنجاح إلى {file_path}")
        return True
        
    except Exception as e:
        logger.error(f"خطأ أثناء تصدير البيانات إلى JSON: {str(e)}")
        return False

def load_json(file_path: str) -> Optional[Dict[str, Any]]:
    """
    تحميل بيانات من ملف JSON.
    
    المعاملات:
        file_path (str): مسار ملف JSON.
        
    العوائد:
        Optional[Dict[str, Any]]: البيانات المحملة أو None في حالة الفشل.
    """
    if not os.path.exists(file_path):
        logger.warning(f"الملف غير موجود: {file_path}")
        return None
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        logger.info(f"تم تحميل البيانات بنجاح من {file_path}")
        return data
        
    except json.JSONDecodeError as e:
        logger.error(f"خطأ في تنسيق JSON: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"خطأ أثناء تحميل البيانات من JSON: {str(e)}")
        return None

def merge_json_files(file_paths: list, output_path: str) -> bool:
    """
    دمج عدة ملفات JSON في ملف واحد.
    
    المعاملات:
        file_paths (list): قائمة بمسارات ملفات JSON.
        output_path (str): مسار ملف الإخراج.
        
    العوائد:
        bool: True إذا نجحت عملية الدمج، False في حالة الفشل.
    """
    if not file_paths:
        logger.warning("لا توجد ملفات للدمج")
        return False
    
    try:
        merged_data = {}
        
        for file_path in file_paths:
            data = load_json(file_path)
            if data:
                # استخراج اسم الملف بدون امتداد كمفتاح
                file_name = os.path.splitext(os.path.basename(file_path))[0]
                merged_data[file_name] = data
        
        if not merged_data:
            logger.warning("لم يتم تحميل أي بيانات من الملفات المحددة")
            return False
        
        # تصدير البيانات المدمجة
        return export_json(merged_data, output_path)
        
    except Exception as e:
        logger.error(f"خطأ أثناء دمج ملفات JSON: {str(e)}")
        return False 

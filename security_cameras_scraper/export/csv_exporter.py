# الملف: security_cameras_scraper/export/csv_exporter.py

"""
أداة لتصدير البيانات المستخرجة بتنسيق CSV.
"""

import os
import csv
import logging
from typing import Dict, Any, List, Optional

from ..utils.data_utils import flatten_dict

logger = logging.getLogger(__name__)

def export_csv(data: Dict[str, Any], 
              file_path: str, 
              delimiter: str = ',', 
              quotechar: str = '"') -> bool:
    """
    تصدير البيانات إلى ملف CSV.
    
    المعاملات:
        data (Dict[str, Any]): البيانات المراد تصديرها.
        file_path (str): مسار الملف للتصدير.
        delimiter (str): الفاصل بين الأعمدة.
        quotechar (str): حرف التنصيص.
        
    العوائد:
        bool: True إذا نجحت عملية التصدير، False في حالة الفشل.
    """
    if not data:
        logger.warning("لا توجد بيانات للتصدير")
        return False
    
    try:
        # تسطيح البيانات المتداخلة
        flattened_data = flatten_dict(data)
        
        if not flattened_data:
            logger.warning("فشل في تسطيح البيانات")
            return False
        
        # التأكد من وجود المجلد الأب
        parent_dir = os.path.dirname(file_path)
        if parent_dir and not os.path.exists(parent_dir):
            os.makedirs(parent_dir)
        
        # استخراج جميع المفاتيح (الأعمدة)
        headers = list(flattened_data.keys())
        
        # تصدير البيانات إلى ملف CSV
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(
                f, 
                fieldnames=headers,
                delimiter=delimiter,
                quotechar=quotechar,
                quoting=csv.QUOTE_MINIMAL
            )
            
            # كتابة رؤوس الأعمدة
            writer.writeheader()
            
            # كتابة الصف الوحيد من البيانات
            writer.writerow(flattened_data)
        
        logger.info(f"تم تصدير البيانات بنجاح إلى {file_path}")
        return True
        
    except Exception as e:
        logger.error(f"خطأ أثناء تصدير البيانات إلى CSV: {str(e)}")
        return False

def export_multi_csv(data_list: List[Dict[str, Any]], 
                    file_path: str, 
                    delimiter: str = ',', 
                    quotechar: str = '"') -> bool:
    """
    تصدير قائمة من البيانات إلى ملف CSV.
    
    المعاملات:
        data_list (List[Dict[str, Any]]): قائمة بالبيانات المراد تصديرها.
        file_path (str): مسار الملف للتصدير.
        delimiter (str): الفاصل بين الأعمدة.
        quotechar (str): حرف التنصيص.
        
    العوائد:
        bool: True إذا نجحت عملية التصدير، False في حالة الفشل.
    """
    if not data_list:
        logger.warning("لا توجد بيانات للتصدير")
        return False
    
    try:
        # تسطيح كل قاموس في القائمة
        flattened_list = []
        all_headers = set()
        
        for data in data_list:
            flattened = flatten_dict(data)
            flattened_list.append(flattened)
            
            # جمع جميع المفاتيح الفريدة
            all_headers.update(flattened.keys())
        
        if not flattened_list:
            logger.warning("فشل في تسطيح البيانات")
            return False
        
        # التأكد من وجود المجلد الأب
        parent_dir = os.path.dirname(file_path)
        if parent_dir and not os.path.exists(parent_dir):
            os.makedirs(parent_dir)
        
        # ترتيب المفاتيح لضمان اتساق الأعمدة
        headers = sorted(list(all_headers))
        
        # تصدير البيانات إلى ملف CSV
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(
                f, 
                fieldnames=headers,
                delimiter=delimiter,
                quotechar=quotechar,
                quoting=csv.QUOTE_MINIMAL,
                restval=''  # القيمة الافتراضية للحقول المفقودة
            )
            
            # كتابة رؤوس الأعمدة
            writer.writeheader()
            
            # كتابة الصفوف
            for row in flattened_list:
                writer.writerow(row)
        
        logger.info(f"تم تصدير البيانات المتعددة بنجاح إلى {file_path}")
        return True
        
    except Exception as e:
        logger.error(f"خطأ أثناء تصدير البيانات المتعددة إلى CSV: {str(e)}")
        return False

def load_csv(file_path: str, delimiter: str = ',') -> Optional[List[Dict[str, str]]]:
    """
    تحميل بيانات من ملف CSV.
    
    المعاملات:
        file_path (str): مسار ملف CSV.
        delimiter (str): الفاصل بين الأعمدة.
        
    العوائد:
        Optional[List[Dict[str, str]]]: البيانات المحملة أو None في حالة الفشل.
    """
    if not os.path.exists(file_path):
        logger.warning(f"الملف غير موجود: {file_path}")
        return None
    
    try:
        rows = []
        with open(file_path, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter=delimiter)
            for row in reader:
                rows.append(dict(row))
        
        logger.info(f"تم تحميل {len(rows)} صف من {file_path}")
        return rows
        
    except Exception as e:
        logger.error(f"خطأ أثناء تحميل البيانات من CSV: {str(e)}")
        return None 

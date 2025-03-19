# الملف: security_cameras_scraper/export/excel_exporter.py

"""
أداة لتصدير البيانات المستخرجة بتنسيق Excel.
"""

import os
import logging
from typing import Dict, Any, List, Optional, Union, Tuple

try:
    import pandas as pd
except ImportError:
    pd = None

from ..utils.data_utils import flatten_dict

logger = logging.getLogger(__name__)

def export_excel(data: Dict[str, Any], 
                file_path: str, 
                sheet_name: str = 'Camera Specs',
                index: bool = False) -> bool:
    """
    تصدير البيانات إلى ملف Excel.
    
    المعاملات:
        data (Dict[str, Any]): البيانات المراد تصديرها.
        file_path (str): مسار الملف للتصدير.
        sheet_name (str): اسم ورقة العمل.
        index (bool): ما إذا كان سيتم عرض الفهرس.
        
    العوائد:
        bool: True إذا نجحت عملية التصدير، False في حالة الفشل.
    """
    if pd is None:
        logger.error("مكتبة pandas غير متوفرة. يرجى تثبيتها باستخدام: pip install pandas openpyxl")
        return False
    
    if not data:
        logger.warning("لا توجد بيانات للتصدير")
        return False
    
    try:
        # تنظيم البيانات وتحويلها إلى تنسيق مناسب لـ Excel
        sections_data = prepare_excel_data(data)
        
        # التأكد من وجود المجلد الأب
        parent_dir = os.path.dirname(file_path)
        if parent_dir and not os.path.exists(parent_dir):
            os.makedirs(parent_dir)
        
        # إنشاء كائن ExcelWriter
        with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
            # كتابة المعلومات العامة في الورقة الأولى
            if 'General information' in sections_data:
                general_df = pd.DataFrame(sections_data['General information'])
                general_df.to_excel(writer, sheet_name='General Info', index=index)
            
            # كتابة كل قسم في ورقة منفصلة
            for section_name, section_data in sections_data.items():
                if section_name != 'General information' and section_data:
                    # تحويل البيانات إلى DataFrame
                    df = pd.DataFrame(section_data)
                    
                    # اسم الورقة يجب ألا يتجاوز 31 حرفاً (قيد Excel)
                    sheet_name = section_name[:31]
                    
                    # تصدير DataFrame إلى ورقة Excel
                    df.to_excel(writer, sheet_name=sheet_name, index=index)
        
        logger.info(f"تم تصدير البيانات بنجاح إلى {file_path}")
        return True
        
    except Exception as e:
        logger.error(f"خطأ أثناء تصدير البيانات إلى Excel: {str(e)}")
        return False

def prepare_excel_data(data: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
    """
    تحضير البيانات بتنسيق مناسب للتصدير إلى Excel.
    
    المعاملات:
        data (Dict[str, Any]): البيانات الأصلية.
        
    العوائد:
        Dict[str, List[Dict[str, Any]]]: البيانات المنظمة حسب الأقسام.
    """
    sections_data = {}
    
    # معالجة المعلومات العامة
    if 'General information' in data:
        general_info = []
        for key, value in data['General information'].items():
            general_info.append({'Property': key, 'Value': value})
        sections_data['General information'] = general_info
    
    # معالجة بقية الأقسام
    for section_name, section_content in data.items():
        if section_name != 'General information':
            section_rows = []
            
            # تحويل محتوى القسم إلى صفوف
            if isinstance(section_content, dict):
                for key, value in section_content.items():
                    # إذا كانت القيمة قاموساً (عنوان فرعي)
                    if isinstance(value, dict):
                        for subkey, subvalue in value.items():
                            section_rows.append({
                                'Category': key,
                                'Property': subkey,
                                'Value': str(subvalue)  # تحويل القيمة إلى نص
                            })
                    # إذا كانت القيمة قائمة (جدول)
                    elif isinstance(value, list) and len(value) > 0 and isinstance(value[0], dict):
                        for i, item in enumerate(value):
                            row_data = {'Category': key, 'Row': i+1}
                            for subkey, subvalue in item.items():
                                row_data[subkey] = subvalue
                            section_rows.append(row_data)
                    # قيمة بسيطة
                    else:
                        section_rows.append({
                            'Category': '',
                            'Property': key,
                            'Value': str(value)  # تحويل القيمة إلى نص
                        })
            
            if section_rows:
                sections_data[section_name] = section_rows
    
    return sections_data

def export_multi_sheet_excel(data_map: Dict[str, Dict[str, Any]], 
                           file_path: str,
                           index: bool = False) -> bool:
    """
    تصدير بيانات متعددة إلى ورقات مختلفة في ملف Excel.
    
    المعاملات:
        data_map (Dict[str, Dict[str, Any]]): خريطة بأسماء الورقات والبيانات المقابلة.
        file_path (str): مسار الملف للتصدير.
        index (bool): ما إذا كان سيتم عرض الفهرس.
        
    العوائد:
        bool: True إذا نجحت عملية التصدير، False في حالة الفشل.
    """
    if pd is None:
        logger.error("مكتبة pandas غير متوفرة. يرجى تثبيتها باستخدام: pip install pandas openpyxl")
        return False
    
    if not data_map:
        logger.warning("لا توجد بيانات للتصدير")
        return False
    
    try:
        # التأكد من وجود المجلد الأب
        parent_dir = os.path.dirname(file_path)
        if parent_dir and not os.path.exists(parent_dir):
            os.makedirs(parent_dir)
        
        # إنشاء كائن ExcelWriter
        with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
            for sheet_name, data in data_map.items():
                # تحضير البيانات لهذه الورقة
                prepared_data = prepare_excel_data(data)
                
                # اسم الورقة يجب ألا يتجاوز 31 حرفاً (قيد Excel)
                valid_sheet_name = sheet_name[:31]
                
                # تصدير المعلومات العامة إن وجدت
                if 'General information' in prepared_data:
                    df = pd.DataFrame(prepared_data['General information'])
                    df.to_excel(writer, sheet_name=f"{valid_sheet_name}_Info", index=index)
                
                # تصدير بقية الأقسام
                section_count = 0
                for section, rows in prepared_data.items():
                    if section != 'General information' and rows:
                        df = pd.DataFrame(rows)
                        section_sheet_name = f"{valid_sheet_name}_{section[:20]}"
                        
                        # إذا كان هناك تكرار في أسماء الأوراق
                        if section_count > 0:
                            section_sheet_name = f"{section_sheet_name}_{section_count}"
                        
                        # تصدير DataFrame إلى ورقة Excel
                        df.to_excel(writer, sheet_name=section_sheet_name[:31], index=index)
                        section_count += 1
        
        logger.info(f"تم تصدير البيانات متعددة الأوراق بنجاح إلى {file_path}")
        return True
        
    except Exception as e:
        logger.error(f"خطأ أثناء تصدير البيانات متعددة الأوراق إلى Excel: {str(e)}")
        return False

def load_excel(file_path: str, sheet_name: Optional[Union[str, int]] = 0) -> Optional[pd.DataFrame]:
    """
    تحميل بيانات من ملف Excel.
    
    المعاملات:
        file_path (str): مسار ملف Excel.
        sheet_name (Optional[Union[str, int]]): اسم أو رقم ورقة العمل.
        
    العوائد:
        Optional[pd.DataFrame]: البيانات المحملة أو None في حالة الفشل.
    """
    if pd is None:
        logger.error("مكتبة pandas غير متوفرة. يرجى تثبيتها باستخدام: pip install pandas openpyxl")
        return None
    
    if not os.path.exists(file_path):
        logger.warning(f"الملف غير موجود: {file_path}")
        return None
    
    try:
        # تحميل البيانات من ملف Excel
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        
        logger.info(f"تم تحميل البيانات بنجاح من {file_path}")
        return df
        
    except Exception as e:
        logger.error(f"خطأ أثناء تحميل البيانات من Excel: {str(e)}")
        return None 

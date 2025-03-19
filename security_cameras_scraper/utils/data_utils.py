# الملف: security_cameras_scraper/utils/data_utils.py

"""
أدوات لمعالجة البيانات المستخرجة.
"""

import re
import logging
from typing import Dict, Any, Optional, List, Union

logger = logging.getLogger(__name__)

def clean_text(text: str) -> str:
    """
    تنظيف النص المستخرج.
    
    المعاملات:
        text (str): النص المراد تنظيفه.
        
    العوائد:
        str: النص بعد التنظيف.
    """
    if not text:
        return ""
    
    try:
        # إزالة المسافات الزائدة في البداية والنهاية
        cleaned = text.strip()
        
        # استبدال المسافات المتعددة بمسافة واحدة
        cleaned = re.sub(r'\s+', ' ', cleaned)
        
        # إزالة أحرف التحكم
        cleaned = re.sub(r'[\x00-\x1F\x7F]', '', cleaned)
        
        # إزالة رموز HTML المشفرة مثل &nbsp;
        cleaned = re.sub(r'&[a-zA-Z]+;', ' ', cleaned)
        
        return cleaned
    except Exception as e:
        logger.debug(f"خطأ أثناء تنظيف النص: {str(e)}")
        return text

def sanitize_key(key: str) -> str:
    """
    تنظيف مفتاح لاستخدامه في قاموس JSON.
    
    المعاملات:
        key (str): المفتاح المراد تنظيفه.
        
    العوائد:
        str: المفتاح بعد التنظيف.
    """
    if not key:
        return ""
    
    try:
        # تحويل المفتاح إلى نص
        key_str = str(key)
        
        # إزالة المسافات الزائدة والأحرف الخاصة
        sanitized = clean_text(key_str)
        
        # استبدال المسافات بالشرطة السفلية
        sanitized = sanitized.replace(' ', '_')
        
        # استبدال الأحرف غير الصالحة بالشرطة السفلية
        sanitized = re.sub(r'[^\w]', '_', sanitized)
        
        # تأكد من أن المفتاح لا يبدأ برقم
        if sanitized and sanitized[0].isdigit():
            sanitized = 'key_' + sanitized
        
        return sanitized
    except Exception as e:
        logger.debug(f"خطأ أثناء تنظيف المفتاح: {str(e)}")
        return str(key)

def organize_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    تنظيم البيانات وتحسين هيكلها.
    
    المعاملات:
        data (Dict[str, Any]): البيانات المراد تنظيمها.
        
    العوائد:
        Dict[str, Any]: البيانات بعد التنظيم.
    """
    if not data:
        return {}
    
    try:
        organized = {}
        
        # نقل قسم "General information" إلى بداية القاموس إن وجد
        if "General information" in data:
            organized["General information"] = data["General information"]
        
        # ترتيب بقية الأقسام أبجدياً
        for section in sorted([s for s in data if s != "General information"]):
            organized[section] = data[section]
        
        # تنظيف مفاتيح القاموس لضمان توافقها مع JSON
        for section, content in organized.items():
            # تجاهل المفاتيح الفارغة
            if not section:
                continue
                
            # تنظيف محتوى الأقسام
            if isinstance(content, dict):
                for key, value in list(content.items()):
                    # تجاهل المفاتيح الفارغة داخل الأقسام
                    if not key:
                        del content[key]
                        continue
                        
                    # إذا كانت القيمة قاموساً، قم بتنظيف مفاتيحه أيضاً
                    if isinstance(value, dict):
                        clean_subsection = {}
                        for subkey, subvalue in value.items():
                            if subkey:  # تجاهل المفاتيح الفارغة
                                clean_subsection[clean_text(subkey)] = subvalue
                        content[key] = clean_subsection
        
        return organized
    except Exception as e:
        logger.error(f"خطأ أثناء تنظيم البيانات: {str(e)}")
        return data

def merge_section_data(sections: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    دمج بيانات من أقسام مختلفة في قاموس واحد.
    
    المعاملات:
        sections (List[Dict[str, Any]]): قائمة بأقسام البيانات المراد دمجها.
        
    العوائد:
        Dict[str, Any]: البيانات المدمجة.
    """
    if not sections:
        return {}
    
    try:
        merged = {}
        
        for section in sections:
            for key, value in section.items():
                if key in merged:
                    # إذا كان المفتاح موجوداً بالفعل وكلاهما قاموس، قم بدمجهما
                    if isinstance(merged[key], dict) and isinstance(value, dict):
                        merged[key].update(value)
                    # إذا كان المفتاح موجوداً ولكن بقيم مختلفة النوع، احتفظ بالقيمة الجديدة
                    else:
                        merged[key] = value
                else:
                    # إضافة المفتاح الجديد مباشرة
                    merged[key] = value
        
        return merged
    except Exception as e:
        logger.error(f"خطأ أثناء دمج البيانات: {str(e)}")
        return {}

def extract_nested_value(data: Dict[str, Any], keys: List[str], default: Any = None) -> Any:
    """
    استخراج قيمة من قاموس متداخل بناءً على مسار المفاتيح.
    
    المعاملات:
        data (Dict[str, Any]): البيانات المراد البحث فيها.
        keys (List[str]): قائمة المفاتيح التي تشكل المسار.
        default (Any): القيمة الافتراضية في حالة عدم وجود المسار.
        
    العوائد:
        Any: القيمة المستخرجة أو القيمة الافتراضية.
    """
    if not data or not keys:
        return default
    
    try:
        current = data
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return default
        return current
    except Exception as e:
        logger.debug(f"خطأ أثناء استخراج قيمة متداخلة: {str(e)}")
        return default

def flatten_dict(data: Dict[str, Any], separator: str = '.') -> Dict[str, Any]:
    """
    تسطيح قاموس متداخل إلى قاموس مسطح.
    
    المعاملات:
        data (Dict[str, Any]): القاموس المراد تسطيحه.
        separator (str): الفاصل بين مستويات المفاتيح.
        
    العوائد:
        Dict[str, Any]: القاموس المسطح.
    """
    if not data:
        return {}
    
    try:
        flattened = {}
        
        def _flatten(d, parent_key=''):
            for key, value in d.items():
                new_key = f"{parent_key}{separator}{key}" if parent_key else key
                
                if isinstance(value, dict):
                    _flatten(value, new_key)
                else:
                    flattened[new_key] = value
        
        _flatten(data)
        return flattened
    except Exception as e:
        logger.error(f"خطأ أثناء تسطيح القاموس: {str(e)}")
        return {} 

# الملف: security_cameras_scraper/utils/html_utils.py

"""
أدوات لتحليل ومعالجة HTML.
"""

import logging
from typing import Optional, List, Any, Union
from bs4 import BeautifulSoup, Tag, NavigableString

logger = logging.getLogger(__name__)

def extract_text(element: Union[Tag, NavigableString, None]) -> str:
    """
    استخراج النص من عنصر HTML بطريقة آمنة.
    
    المعاملات:
        element (Union[Tag, NavigableString, None]): عنصر HTML.
        
    العوائد:
        str: النص المستخرج أو سلسلة فارغة في حالة الفشل.
    """
    if element is None:
        return ""
    
    try:
        text = element.get_text(strip=True)
        return text
    except (AttributeError, TypeError) as e:
        logger.debug(f"خطأ أثناء استخراج النص: {str(e)}")
        
        # معالجة النص المباشر
        if isinstance(element, str) or isinstance(element, NavigableString):
            return str(element).strip()
        
        return ""

def get_element_by_selector(soup: Union[BeautifulSoup, Tag], 
                          selector: str, 
                          default: Any = None) -> Optional[Tag]:
    """
    استخراج عنصر HTML باستخدام CSS selector.
    
    المعاملات:
        soup (Union[BeautifulSoup, Tag]): كائن BeautifulSoup أو Tag.
        selector (str): محدد CSS.
        default (Any): القيمة الافتراضية في حالة عدم وجود عنصر.
        
    العوائد:
        Optional[Tag]: العنصر المستخرج أو القيمة الافتراضية.
    """
    if not soup or not selector:
        return default
    
    try:
        element = soup.select_one(selector)
        return element if element else default
    except Exception as e:
        logger.debug(f"خطأ أثناء استخراج العنصر بواسطة {selector}: {str(e)}")
        return default

def get_elements_by_selector(soup: Union[BeautifulSoup, Tag], 
                           selector: str) -> List[Tag]:
    """
    استخراج قائمة عناصر HTML باستخدام CSS selector.
    
    المعاملات:
        soup (Union[BeautifulSoup, Tag]): كائن BeautifulSoup أو Tag.
        selector (str): محدد CSS.
        
    العوائد:
        List[Tag]: قائمة العناصر المستخرجة.
    """
    if not soup or not selector:
        return []
    
    try:
        elements = soup.select(selector)
        return elements
    except Exception as e:
        logger.debug(f"خطأ أثناء استخراج العناصر بواسطة {selector}: {str(e)}")
        return []

def get_element_attribute(element: Tag, attribute: str, default: str = "") -> str:
    """
    استخراج قيمة سمة من عنصر HTML.
    
    المعاملات:
        element (Tag): عنصر HTML.
        attribute (str): اسم السمة.
        default (str): القيمة الافتراضية في حالة عدم وجود السمة.
        
    العوائد:
        str: قيمة السمة.
    """
    if not element or not attribute:
        return default
    
    try:
        value = element.get(attribute)
        return value if value else default
    except Exception as e:
        logger.debug(f"خطأ أثناء استخراج السمة {attribute}: {str(e)}")
        return default

def parse_table(table_element: Tag) -> List[List[str]]:
    """
    تحليل جدول HTML واستخراج محتواه كمصفوفة.
    
    المعاملات:
        table_element (Tag): عنصر جدول HTML.
        
    العوائد:
        List[List[str]]: البيانات المستخرجة من الجدول.
    """
    if not table_element:
        return []
    
    try:
        rows = []
        # البحث عن صفوف في tbody أو tr مباشرة
        tr_elements = table_element.find_all('tr')
        
        for tr in tr_elements:
            row_data = []
            # العثور على جميع خلايا th و td
            cells = tr.find_all(['th', 'td'])
            
            for cell in cells:
                # استخراج النص من الخلية
                cell_text = extract_text(cell)
                row_data.append(cell_text)
            
            if row_data:  # تجاهل الصفوف الفارغة
                rows.append(row_data)
        
        return rows
    except Exception as e:
        logger.debug(f"خطأ أثناء تحليل الجدول: {str(e)}")
        return []

def extract_meta_tags(soup: BeautifulSoup) -> dict:
    """
    استخراج معلومات من وسوم meta في HTML.
    
    المعاملات:
        soup (BeautifulSoup): كائن BeautifulSoup.
        
    العوائد:
        dict: قاموس بمعلومات meta.
    """
    meta_data = {}
    
    try:
        # استخراج جميع وسوم meta
        meta_tags = soup.find_all('meta')
        
        for tag in meta_tags:
            name = tag.get('name') or tag.get('property')
            content = tag.get('content')
            
            if name and content:
                meta_data[name] = content
        
        return meta_data
    except Exception as e:
        logger.debug(f"خطأ أثناء استخراج وسوم meta: {str(e)}")
        return meta_data 

# الملف: security_cameras_scraper/scrapers/dahua_scraper.py

"""
مستخرج بيانات منتجات Dahua.
"""

import logging
from typing import Dict, Any, Optional, List
from bs4 import BeautifulSoup, Tag

from ..utils.html_utils import (
    extract_text, 
    get_element_by_selector, 
    get_elements_by_selector
)
from ..utils.data_utils import clean_text, organize_data

logger = logging.getLogger(__name__)


class DahuaScraper:
    """
    مستخرج مخصص لاستخراج بيانات منتجات Dahua.
    """
    
    def __init__(self):
        """تهيئة مستخرج Dahua."""
        self.name = "Dahua"
    
    def extract(self, html_content: str, url: str) -> Dict[str, Any]:
        """
        استخراج بيانات منتج Dahua من HTML.
        
        المعاملات:
            html_content (str): محتوى HTML للصفحة.
            url (str): رابط الصفحة (للرجوع).
            
        العوائد:
            Dict[str, Any]: البيانات المستخرجة منظمة.
        """
        try:
            soup = BeautifulSoup(html_content, 'lxml')
            structured_data = {}
            
            # استخراج المعلومات العامة
            self._extract_general_information(soup, structured_data)
            
            # استخراج المواصفات التقنية
            self._extract_technical_specifications(soup, structured_data)
            
            return structured_data
            
        except Exception as e:
            logger.error(f"خطأ أثناء استخراج بيانات Dahua: {str(e)}")
            return {"error": str(e)}
    
    def _extract_general_information(self, soup: BeautifulSoup, data: Dict[str, Any]) -> None:
        """
        استخراج المعلومات العامة للمنتج.
        
        المعاملات:
            soup (BeautifulSoup): كائن BeautifulSoup.
            data (Dict[str, Any]): قاموس البيانات للتحديث.
        """
        # إضافة قسم للمعلومات العامة
        data["General information"] = {}
        
        # استخراج بيانات من div معين
        main_data = get_elements_by_selector(soup, "div.el-row")
        
        # البحث داخل كل div عن h3 و p لاستخراج معلومات المنتج الأساسية
        product_title = None
        product_type = None
        
        for div in main_data:
            title = get_element_by_selector(div, "h3.title")
            camera_type = get_element_by_selector(div, "p.text")
            
            if title:
                product_title = extract_text(title)
            if camera_type:
                product_type = extract_text(camera_type)
        
        # إضافة البيانات المستخرجة إلى القسم العام
        if product_title:
            data["General information"]["Product Title"] = product_title
            logger.debug(f"تم استخراج عنوان المنتج: {product_title}")
        else:
            logger.warning("لم يتم العثور على عنوان المنتج")
        
        if product_type:
            data["General information"]["Product Type"] = product_type
            logger.debug(f"تم استخراج نوع المنتج: {product_type}")
        else:
            logger.warning("لم يتم العثور على نوع المنتج")
    
    def _extract_technical_specifications(self, soup: BeautifulSoup, data: Dict[str, Any]) -> None:
        """
        استخراج المواصفات التقنية للمنتج.
        
        المعاملات:
            soup (BeautifulSoup): كائن BeautifulSoup.
            data (Dict[str, Any]): قاموس البيانات للتحديث.
        """
        # البحث عن جميع الجداول في الصفحة
        tables = soup.find_all("table")
        
        if not tables:
            logger.warning("لم يتم العثور على جداول للمواصفات")
            return
            
        logger.info(f"تم العثور على {len(tables)} جدول في صفحة Dahua")
        
        current_section = None
        current_key = None
        table_headers = {}  # قاموس لتخزين رؤوس الأعمدة لكل مفتاح
        
        for table in tables:
            rows = table.find_all("tr")
            
            for row in rows:
                cells = row.find_all("td")
                
                # تجاهل الصفوف الفارغة
                if not cells:
                    continue
                
                # إذا كان هناك عمود واحد فقط
                if len(cells) == 1:
                    cell_text = extract_text(cells[0])
                    
                    # تحقق ما إذا كان النص هو اسم قسم أو فقرة شرحية
                    if "DORI" in cell_text and any(keyword in cell_text.lower() for keyword in ["standard system", "ability", "distinguish", "en-62676-4"]):
                        # تجاهل الفقرات الشرحية
                        continue
                    elif len(cell_text) > 100:  # فقرة طويلة غالباً تكون شرحية
                        # تجاهل الفقرات الشرحية الطويلة
                        continue
                    else:
                        # هذا قسم رئيسي جديد
                        current_section = clean_text(cell_text)
                        if current_section not in data:
                            data[current_section] = {}
                        current_key = None
                
                # إذا كان أول `<td>` يحتوي على `rowspan`، فهو مفتاح جديد
                elif len(cells) > 1 and cells[0].has_attr("rowspan"):
                    current_key = clean_text(extract_text(cells[0]))
                    
                    # استخراج رؤوس الأعمدة من الصف الأول
                    headers = [
                        clean_text(extract_text(cell)) 
                        for cell in cells 
                        if not cell.has_attr("rowspan") and not extract_text(cell).startswith("DORI")
                    ]
                    
                    # تخزين رؤوس الأعمدة في قاموس منفصل للاستخدام لاحقاً
                    if current_section and current_key:
                        table_headers[f"{current_section}_{current_key}"] = headers
                        
                        # إنشاء قائمة فارغة لتخزين صفوف البيانات
                        data[current_section][current_key] = []
                
                # إذا كان هناك `colspan` في الصف، فهذا يعني أنه تابع للمفتاح `rowspan` الحالي
                elif any(cell.has_attr("colspan") for cell in cells) and current_section and current_key:
                    header_key = f"{current_section}_{current_key}"
                    
                    if header_key in table_headers:
                        values = [
                            clean_text(extract_text(cell)) 
                            for cell in cells 
                            if cell.has_attr("colspan") and not extract_text(cell).startswith("DORI")
                        ]
                        
                        # استرجاع رؤوس الأعمدة للمفتاح الحالي
                        headers = table_headers[header_key]
                        row_dict = {}
                        
                        # دمج رؤوس الأعمدة مع القيم المقابلة لها
                        for i, value in enumerate(values):
                            if i < len(headers):
                                row_dict[headers[i]] = value
                            else:
                                row_dict[f"column_{i}"] = value
                        
                        # إضافة الصف المنسق إلى قائمة صفوف البيانات
                        if row_dict:
                            data[current_section][current_key].append(row_dict)
                
                # إذا لم يكن هناك `rowspan` أو `colspan`، فهو مفتاح عادي مع قيمة
                elif len(cells) == 2 and current_section:
                    key = clean_text(extract_text(cells[0]))
                    value = clean_text(extract_text(cells[1]))
                    
                    if key and current_section in data:
                        data[current_section][key] = value
        
        # تنظيف البيانات بعد الاستخراج
        self._clean_data_structure(data)
    
    def _clean_data_structure(self, data: Dict[str, Any]) -> None:
        """
        تنظيف هيكل البيانات بعد الاستخراج.
        
        المعاملات:
            data (Dict[str, Any]): قاموس البيانات للتنظيف.
        """
        # إزالة الأقسام الفارغة
        sections_to_remove = []
        
        for section, content in data.items():
            if section != "General information" and (not content or len(content) == 0):
                sections_to_remove.append(section)
        
        for section in sections_to_remove:
            data.pop(section, None)
        
        # تحويل القوائم الفارغة إلى قواميس
        for section, content in data.items():
            for key, value in content.items():
                if isinstance(value, list) and len(value) == 0:
                    data[section][key] = {}
                    
        # تنظيف الأسماء (إزالة المسافات الزائدة والأحرف الخاصة)
        clean_data = {}
        
        for section, content in data.items():
            clean_section = clean_text(section)
            clean_data[clean_section] = {}
            
            for key, value in content.items():
                clean_key = clean_text(key)
                clean_data[clean_section][clean_key] = value
        
        # تحديث البيانات الأصلية بالبيانات النظيفة
        data.clear()
        data.update(clean_data)
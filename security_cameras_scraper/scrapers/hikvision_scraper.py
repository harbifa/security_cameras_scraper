 
# الملف: security_cameras_scraper/scrapers/hikvision_scraper.py

"""
مستخرج بيانات منتجات Hikvision.
"""

import logging
from typing import Dict, Any, Optional, List
from bs4 import BeautifulSoup

from ..utils.html_utils import (
    extract_text, 
    get_element_by_selector, 
    get_elements_by_selector
)
from ..utils.data_utils import clean_text, organize_data

logger = logging.getLogger(__name__)


class HikvisionScraper:
    """
    مستخرج مخصص لاستخراج بيانات منتجات Hikvision.
    """
    
    def __init__(self):
        """تهيئة مستخرج Hikvision."""
        self.name = "Hikvision"
    
    def extract(self, html_content: str, url: str) -> Dict[str, Any]:
        """
        استخراج بيانات منتج Hikvision من HTML.
        
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
            sections_extracted = self._extract_technical_specifications(soup, structured_data)
            
            # إذا لم يتم استخراج أي مواصفات، جرب الطريقة البديلة
            if not sections_extracted:
                logger.info("استخدام طريقة بديلة لاستخراج المواصفات التقنية")
                self._extract_technical_specifications_alternative(soup, structured_data)
            
            return structured_data
            
        except Exception as e:
            logger.error(f"خطأ أثناء استخراج بيانات Hikvision: {str(e)}")
            return {"error": str(e)}
    
    def _extract_general_information(self, soup: BeautifulSoup, data: Dict[str, Any]) -> None:
        """
        استخراج المعلومات العامة للمنتج.
        
        المعاملات:
            soup (BeautifulSoup): كائن BeautifulSoup.
            data (Dict[str, Any]): قاموس البيانات للتحديث.
        """
        # إضافة قسم "General information"
        data["General information"] = {}
        
        # استخراج عنوان المنتج
        product_title_elem = get_element_by_selector(
            soup, 
            "div.product_description_title_tag_container > div.product_description_title > h2"
        )
        
        if product_title_elem:
            product_title = extract_text(product_title_elem)
            data["General information"]["Product Title"] = product_title
            logger.debug(f"تم استخراج عنوان المنتج: {product_title}")
        else:
            logger.warning("لم يتم العثور على عنوان المنتج")
        
        # استخراج نوع المنتج
        product_type_elem = get_element_by_selector(
            soup, 
            "div > div.product-description-container > div > h1"
        )
        
        if product_type_elem:
            product_type = extract_text(product_type_elem)
            data["General information"]["Product Type"] = product_type
            logger.debug(f"تم استخراج نوع المنتج: {product_type}")
        else:
            logger.warning("لم يتم العثور على نوع المنتج")
    
    def _extract_technical_specifications(self, soup: BeautifulSoup, data: Dict[str, Any]) -> bool:
        """
        استخراج المواصفات التقنية للمنتج.
        
        المعاملات:
            soup (BeautifulSoup): كائن BeautifulSoup.
            data (Dict[str, Any]): قاموس البيانات للتحديث.
            
        العوائد:
            bool: True إذا تم استخراج أي أقسام، False خلاف ذلك.
        """
        # استخراج العناوين الرئيسية (الأقسام)
        section_uls = get_elements_by_selector(soup, "ul.tech-specs-items-description[data-target]")
        
        if not section_uls:
            logger.warning("لم يتم العثور على أقسام المواصفات التقنية")
            return False
        
        logger.info(f"تم العثور على {len(section_uls)} قسم رئيسي")
        
        sections_count = 0
        
        # لكل قسم رئيسي
        for section_ul in section_uls:
            # استخراج اسم القسم من سمة data-target
            section_name = section_ul.get("data-target")
            if not section_name:
                continue
                
            logger.debug(f"استخراج البيانات من قسم: {section_name}")
            
            # إنشاء قاموس لتخزين مواصفات هذا القسم
            data[section_name] = {}
            
            # استخراج عناصر li التي تحتوي على المواصفات في هذا القسم
            spec_items = get_elements_by_selector(section_ul, "li.tech-specs-items-description-list")
            
            if not spec_items:
                logger.warning(f"لم يتم العثور على مواصفات في قسم: {section_name}")
                continue
                
            logger.debug(f"تم العثور على {len(spec_items)} مواصفة في قسم {section_name}")
            
            # متغير لتتبع العنوان الفرعي الحالي
            current_subsection = None
            
            # لكل عنصر li (مواصفة)
            for item in spec_items:
                # استخراج العنوان الفرعي إن وجد
                heading_elem = get_element_by_selector(item, "span.tech-specs-items-description__title--heading")
                if heading_elem:
                    current_subsection = extract_text(heading_elem)
                    # إذا كان العنوان الفرعي مختلف عن اسم القسم، نضيفه كمفتاح جديد
                    if current_subsection and current_subsection != section_name:
                        data[section_name][current_subsection] = {}
                    continue
                
                # استخراج المفتاح والقيمة
                key_elem = get_element_by_selector(item, "span.tech-specs-items-description__title")
                value_elem = get_element_by_selector(item, "span.tech-specs-items-description__title-details")
                
                if key_elem and value_elem:
                    key = clean_text(extract_text(key_elem))
                    value = clean_text(extract_text(value_elem))
                    
                    # إذا كان العنوان الفرعي الحالي موجود ومختلف عن اسم القسم
                    if current_subsection and current_subsection != section_name and current_subsection in data[section_name]:
                        # أضف المفتاح والقيمة تحت العنوان الفرعي
                        data[section_name][current_subsection][key] = value
                    else:
                        # أضف المفتاح والقيمة مباشرة تحت القسم
                        data[section_name][key] = value
            
            sections_count += 1
        
        return sections_count > 0
    
    def _extract_technical_specifications_alternative(self, soup: BeautifulSoup, data: Dict[str, Any]) -> None:
        """
        طريقة بديلة لاستخراج المواصفات التقنية عند فشل الطريقة الأساسية.
        
        المعاملات:
            soup (BeautifulSoup): كائن BeautifulSoup.
            data (Dict[str, Any]): قاموس البيانات للتحديث.
        """
        # الطريقة البديلة - استخدام نفس المنطق ولكن مع جميع العناصر
        all_li_elements = get_elements_by_selector(soup, "li.tech-specs-items-description-list")
        
        if not all_li_elements:
            logger.warning("لم يتم العثور على أي مواصفات تقنية باستخدام الطريقة البديلة")
            return
            
        logger.info(f"تم العثور على {len(all_li_elements)} عنصر li.tech-specs-items-description-list في الصفحة")
        
        current_section = "General"
        current_subsection = None
        
        for li in all_li_elements:
            # التحقق من وجود عنوان قسم جديد
            parent_ul = li.find_parent("ul", class_="tech-specs-items-description")
            if parent_ul and parent_ul.has_attr("data-target"):
                current_section = parent_ul.get("data-target")
                if current_section not in data:
                    data[current_section] = {}
            
            # التحقق من وجود عنوان فرعي
            heading_elem = get_element_by_selector(li, "span.tech-specs-items-description__title--heading")
            if heading_elem:
                current_subsection = extract_text(heading_elem)
                # نتأكد من عدم تكرار الاسم
                if current_subsection and current_subsection != current_section:
                    data[current_section][current_subsection] = {}
                continue
            
            # استخراج المفتاح والقيمة
            key_elem = get_element_by_selector(li, "span.tech-specs-items-description__title")
            value_elem = get_element_by_selector(li, "span.tech-specs-items-description__title-details")
            
            if key_elem and value_elem:
                key = clean_text(extract_text(key_elem))
                value = clean_text(extract_text(value_elem))
                
                # إضافة البيانات في المكان المناسب، تجنباً للتكرار
                if current_subsection and current_subsection != current_section and current_subsection in data[current_section]:
                    data[current_section][current_subsection][key] = value
                else:
                    data[current_section][key] = value
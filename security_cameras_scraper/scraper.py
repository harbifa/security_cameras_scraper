 
# الملف: security_cameras_scraper/scraper.py

"""
الكلاس الرئيسي للمكتبة المسؤول عن إدارة عمليات استخراج البيانات.
"""

import re
import logging
from typing import Dict, Any, Optional, List, Type

from .scrapers.hikvision_scraper import HikvisionScraper
from .scrapers.dahua_scraper import DahuaScraper
from .utils.http_utils import fetch_page
from .export.json_exporter import export_json
from .export.csv_exporter import export_csv
from .export.excel_exporter import export_excel

# إعداد تسجيل الأحداث
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


class CameraScraper:
    """
    الكلاس الرئيسي لاستخراج بيانات كاميرات المراقبة.
    
    يوفر هذا الكلاس واجهة موحدة للتعامل مع مختلف مواقع الشركات المصنعة 
    ويتعرف تلقائيًا على الشركة المناسبة بناءً على الرابط.
    """
    
    def __init__(self, use_default_headers: bool = True):
        """
        تهيئة المستخرج.
        
        المعاملات:
            use_default_headers (bool): ما إذا كان سيتم استخدام الرؤوس الافتراضية لطلبات HTTP.
        """
        self.scrapers = {
            'hikvision': HikvisionScraper(),
            'dahua': DahuaScraper()
        }
        
        self.default_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        } if use_default_headers else {}
    
    def detect_manufacturer(self, url: str) -> Optional[str]:
        """
        التعرف على الشركة المصنعة بناءً على عنوان URL.
        
        المعاملات:
            url (str): رابط صفحة المنتج.
            
        العوائد:
            Optional[str]: اسم الشركة المصنعة أو None إذا لم يتم التعرف عليها.
        """
        url_lower = url.lower()
        
        for manufacturer in self.scrapers.keys():
            if manufacturer in url_lower:
                logger.info(f"تم التعرف على الشركة المصنعة: {manufacturer}")
                return manufacturer
        
        logger.warning(f"لم يتم التعرف على الشركة المصنعة للرابط: {url}")
        return None
    
    def add_manufacturer_scraper(self, manufacturer_name: str, scraper_instance: Any) -> None:
        """
        إضافة مستخرج لشركة مصنعة جديدة.
        
        المعاملات:
            manufacturer_name (str): اسم الشركة المصنعة.
            scraper_instance (Any): كائن المستخرج المخصص للشركة.
        """
        self.scrapers[manufacturer_name.lower()] = scraper_instance
        logger.info(f"تمت إضافة مستخرج جديد للشركة: {manufacturer_name}")
    
    def scrape(self, url: str, headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        استخراج بيانات منتج من الرابط المحدد.
        
        المعاملات:
            url (str): رابط صفحة المنتج.
            headers (Optional[Dict[str, str]]): رؤوس HTTP مخصصة (اختياري).
            
        العوائد:
            Dict[str, Any]: البيانات المستخرجة.
            
        الاستثناءات:
            ValueError: إذا لم يتم التعرف على الشركة المصنعة.
        """
        manufacturer = self.detect_manufacturer(url)
        
        if not manufacturer:
            raise ValueError(f"الشركة المصنعة غير مدعومة أو غير معروفة للرابط: {url}")
        
        # استخدام الرؤوس المخصصة أو الافتراضية
        request_headers = headers or self.default_headers
        
        # استخراج HTML
        html_content = fetch_page(url, request_headers)
        
        if not html_content:
            logger.error(f"فشل في استرجاع محتوى الصفحة: {url}")
            return {}
        
        # استدعاء المستخرج المناسب
        data = self.scrapers[manufacturer].extract(html_content, url)
        
        # ضمان وجود بيانات أساسية
        if not data:
            logger.warning(f"لم يتم استخراج أي بيانات من الرابط: {url}")
            return {}
            
        # إضافة معلومات مرجعية للرابط
        if 'General information' not in data:
            data['General information'] = {}
        
        data['General information']['Source URL'] = url
        data['General information']['Manufacturer'] = manufacturer.capitalize()
        
        return data
    
    def scrape_multiple(self, urls: List[str], headers: Optional[Dict[str, str]] = None) -> Dict[str, Dict[str, Any]]:
        """
        استخراج بيانات من عدة روابط.
        
        المعاملات:
            urls (List[str]): قائمة روابط المنتجات.
            headers (Optional[Dict[str, str]]): رؤوس HTTP مخصصة (اختياري).
            
        العوائد:
            Dict[str, Dict[str, Any]]: قاموس بالبيانات المستخرجة لكل رابط.
        """
        results = {}
        
        for url in urls:
            try:
                results[url] = self.scrape(url, headers)
            except Exception as e:
                logger.error(f"خطأ أثناء استخراج البيانات من {url}: {str(e)}")
                results[url] = {"error": str(e)}
        
        return results
    
    def export_to_json(self, data: Dict[str, Any], file_path: str) -> bool:
        """
        تصدير البيانات إلى ملف JSON.
        
        المعاملات:
            data (Dict[str, Any]): البيانات المراد تصديرها.
            file_path (str): مسار الملف للتصدير.
            
        العوائد:
            bool: True إذا نجحت عملية التصدير، False في حالة الفشل.
        """
        return export_json(data, file_path)
    
    def export_to_csv(self, data: Dict[str, Any], file_path: str) -> bool:
        """
        تصدير البيانات إلى ملف CSV.
        
        المعاملات:
            data (Dict[str, Any]): البيانات المراد تصديرها.
            file_path (str): مسار الملف للتصدير.
            
        العوائد:
            bool: True إذا نجحت عملية التصدير، False في حالة الفشل.
        """
        return export_csv(data, file_path)
    
    def export_to_excel(self, data: Dict[str, Any], file_path: str) -> bool:
        """
        تصدير البيانات إلى ملف Excel.
        
        المعاملات:
            data (Dict[str, Any]): البيانات المراد تصديرها.
            file_path (str): مسار الملف للتصدير.
            
        العوائد:
            bool: True إذا نجحت عملية التصدير، False في حالة الفشل.
        """
        return export_excel(data, file_path)
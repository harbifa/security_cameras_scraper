# الملف: security_cameras_scraper/utils/http_utils.py

"""
أدوات للتعامل مع طلبات HTTP.
"""

import os
import time
import logging
import requests
from typing import Dict, Optional, Union, Any

logger = logging.getLogger(__name__)

def fetch_page(url: str, 
               headers: Optional[Dict[str, str]] = None,
               timeout: int = 30,
               verify_ssl: bool = True) -> Optional[str]:
    """
    استرجاع محتوى صفحة ويب.
    
    المعاملات:
        url (str): رابط الصفحة المراد استرجاعها.
        headers (Optional[Dict[str, str]]): رؤوس HTTP (اختياري).
        timeout (int): مهلة الاتصال بالثواني.
        verify_ssl (bool): التحقق من شهادة SSL.
        
    العوائد:
        Optional[str]: محتوى الصفحة أو None في حالة الفشل.
    """
    default_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    }
    
    # استخدام الرؤوس المخصصة أو الافتراضية
    request_headers = headers or default_headers
    
    try:
        logger.info(f"جاري استرجاع الصفحة: {url}")
        response = requests.get(
            url, 
            headers=request_headers, 
            timeout=timeout,
            verify=verify_ssl
        )
        
        if response.status_code != 200:
            logger.error(f"فشل في استرجاع الصفحة. رمز الحالة: {response.status_code}")
            return None
            
        # التحقق من وجود محتوى
        if not response.text or len(response.text) < 100:
            logger.warning(f"محتوى الصفحة فارغ أو قصير جداً (الحجم: {len(response.text)} حرف)")
        
        return response.text
        
    except requests.exceptions.Timeout:
        logger.error(f"انتهت مهلة الاتصال للرابط: {url}")
        return None
    except requests.exceptions.ConnectionError:
        logger.error(f"خطأ في الاتصال بالرابط: {url}")
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"خطأ عام في طلب HTTP: {str(e)}")
        return None

def fetch_with_retry(url: str, 
                    headers: Optional[Dict[str, str]] = None, 
                    max_retries: int = 3, 
                    timeout: int = 30,
                    retry_delay: int = 2) -> Optional[str]:
    """
    استرجاع محتوى صفحة ويب مع إعادة المحاولة عند الفشل.
    
    المعاملات:
        url (str): رابط الصفحة المراد استرجاعها.
        headers (Optional[Dict[str, str]]): رؤوس HTTP (اختياري).
        max_retries (int): الحد الأقصى لعدد مرات إعادة المحاولة.
        timeout (int): مهلة الاتصال بالثواني.
        retry_delay (int): التأخير بالثواني بين المحاولات.
        
    العوائد:
        Optional[str]: محتوى الصفحة أو None في حالة الفشل.
    """
    for attempt in range(max_retries):
        logger.info(f"محاولة استرجاع {url} (محاولة {attempt+1}/{max_retries})")
        
        result = fetch_page(url, headers, timeout)
        
        if result:
            return result
            
        if attempt < max_retries - 1:
            wait_time = retry_delay * (2 ** attempt)  # تأخير متزايد
            logger.info(f"الانتظار {wait_time} ثانية قبل المحاولة التالية")
            time.sleep(wait_time)
    
    logger.error(f"فشلت جميع المحاولات لاسترجاع {url}")
    return None

def save_html_sample(html: str, file_path: str, max_size: int = 100000) -> bool:
    """
    حفظ عينة من HTML للفحص.
    
    المعاملات:
        html (str): محتوى HTML المراد حفظه.
        file_path (str): مسار الملف للحفظ.
        max_size (int): الحد الأقصى لحجم الملف بالبايت.
        
    العوائد:
        bool: True إذا تم الحفظ بنجاح، False في حالة الفشل.
    """
    try:
        # التأكد من وجود المجلد الأب
        parent_dir = os.path.dirname(file_path)
        if parent_dir and not os.path.exists(parent_dir):
            os.makedirs(parent_dir)
        
        # اقتطاع المحتوى إذا كان حجمه أكبر من الحد الأقصى
        sample = html[:max_size] if len(html) > max_size else html
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(sample)
            
        logger.info(f"تم حفظ عينة HTML في {file_path}")
        return True
        
    except Exception as e:
        logger.error(f"خطأ أثناء حفظ عينة HTML: {str(e)}")
        return False

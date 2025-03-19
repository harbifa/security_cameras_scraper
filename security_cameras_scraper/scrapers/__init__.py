# الملف: security_cameras_scraper/scrapers/__init__.py

"""
حزمة المستخرجات المخصصة للشركات المصنعة المختلفة.
"""

from .hikvision_scraper import HikvisionScraper
from .dahua_scraper import DahuaScraper

__all__ = ['HikvisionScraper', 'DahuaScraper']

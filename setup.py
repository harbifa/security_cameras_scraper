from setuptools import setup, find_packages

setup(
    name="security_cameras_scraper",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="مكتبة Python لاستخراج بيانات منتجات كاميرات المراقبة من مواقع الشركات المصنعة",
    packages=find_packages(),  # هذا سيجد المجلد الفرعي security_cameras_scraper
    python_requires=">=3.6",
    install_requires=[
        "requests>=2.25.0",
        "beautifulsoup4>=4.9.3",
        "lxml>=4.6.0",
        "pandas>=1.2.0",
        "openpyxl>=3.0.0",
    ],
)
import os

# MySQL bağlantı bilgileri
db_config = {
    'host': os.getenv('MYSQL_ADDON_HOST'),
    'user': os.getenv('MYSQL_ADDON_USER'),
    'password': os.getenv('MYSQL_ADDON_PASSWORD'),
    'database': os.getenv('MYSQL_ADDON_DB'),
    'port': int(os.getenv('MYSQL_ADDON_PORT', 3306)),
    'connect_timeout': 30
}

# Flask uygulama ayarları
class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'gizli-anahtar-buraya')
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    TEMPLATES_FOLDER = '../frontend/templates'
    STATIC_FOLDER = '../frontend/static'
    
    # Rate limit ayarları
    RATELIMIT_DEFAULT = os.getenv('RATELIMIT_DEFAULT', "200 per day")
    RATELIMIT_STORAGE_URL = os.getenv('RATELIMIT_STORAGE_URL', "memory://") 
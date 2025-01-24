import os

# MySQL bağlantı bilgileri
db_config = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'ders_otomata')
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
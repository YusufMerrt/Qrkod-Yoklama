import os

# MySQL bağlantı bilgileri
db_config = {
    'host': os.getenv('DB_HOST', 'bl7gipo0tvedawt6ko8o-mysql.services.clever-cloud.com'),
    'user': os.getenv('DB_USER', 'urvls9oozleh8bgn'),
    'password': os.getenv('DB_PASSWORD', 'QUpVyAiGK2KpgTIe6G2r'),
    'database': os.getenv('DB_NAME', 'bl7gipo0tvedawt6ko8o'),
    'port': 3306,
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
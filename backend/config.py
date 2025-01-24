# MySQL bağlantı bilgileri
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'ders_otomata'
}

# Flask uygulama ayarları
class Config:
    SECRET_KEY = 'gizli-anahtar-buraya'  # Güvenlik için değiştirin
    DEBUG = True
    TEMPLATES_FOLDER = '../frontend/templates'
    STATIC_FOLDER = '../frontend/static'
    
    # Rate limit ayarları
    RATELIMIT_DEFAULT = "200 per day"
    RATELIMIT_STORAGE_URL = "memory://" 
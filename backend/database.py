import mysql.connector
from datetime import datetime
import re
from config import db_config
import time

def get_db_connection(max_retries=3, retry_delay=5):
    """Veritabanı bağlantısı oluşturur"""
    for attempt in range(max_retries):
        try:
            conn = mysql.connector.connect(**db_config)
            return conn
        except mysql.connector.Error as err:
            if attempt < max_retries - 1:
                print(f"Veritabanı bağlantı hatası: {err}")
                print(f"{retry_delay} saniye sonra tekrar denenecek...")
                time.sleep(retry_delay)
            else:
                print(f"Veritabanı bağlantısı başarısız: {err}")
                raise err

def close_db_connection(conn, cursor=None):
    """Veritabanı bağlantısını kapatır"""
    try:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    except mysql.connector.Error as err:
        print(f"Veritabanı bağlantısı kapatılırken hata: {err}")

def init_db(max_retries=3, retry_delay=5):
    """Veritabanı oluşturur"""
    for attempt in range(max_retries):
        try:
            print("Veritabanına bağlanılıyor...")
            conn = get_db_connection()
            cursor = conn.cursor()
            
            print("Tablolar oluşturuluyor...")
            # Bölümler tablosu
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS bolumler (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    bolum_adi VARCHAR(100) NOT NULL,
                    klasor_adi VARCHAR(100) NOT NULL,
                    olusturma_tarihi DATETIME NOT NULL,
                    INDEX idx_bolum_adi (bolum_adi)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            
            # Dersler tablosu (bölüme bağlı)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS dersler (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    bolum_id INT NOT NULL,
                    ders_adi VARCHAR(100) NOT NULL,
                    klasor_adi VARCHAR(100) NOT NULL,
                    olusturma_tarihi DATETIME NOT NULL,
                    INDEX idx_ders_adi (ders_adi),
                    INDEX idx_bolum_id (bolum_id),
                    FOREIGN KEY (bolum_id) REFERENCES bolumler(id) ON DELETE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            
            # Haftalar tablosu (derse bağlı)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS haftalar (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    ders_id INT NOT NULL,
                    hafta_no INT NOT NULL,
                    olusturma_tarihi DATETIME NOT NULL,
                    INDEX idx_ders_id (ders_id),
                    INDEX idx_hafta_no (hafta_no),
                    FOREIGN KEY (ders_id) REFERENCES dersler(id) ON DELETE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            
            # Yoklamalar tablosu (haftaya bağlı)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS yoklamalar (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    hafta_id INT NOT NULL,
                    ad VARCHAR(50) NOT NULL,
                    soyad VARCHAR(50) NOT NULL,
                    ogrenci_no VARCHAR(11) NOT NULL,
                    kayit_tarihi DATETIME NOT NULL,
                    qr_kod_id VARCHAR(50) NOT NULL,
                    INDEX idx_hafta_id (hafta_id),
                    INDEX idx_ogrenci_no (ogrenci_no),
                    INDEX idx_kayit_tarihi (kayit_tarihi),
                    FOREIGN KEY (hafta_id) REFERENCES haftalar(id) ON DELETE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            
            conn.commit()
            print("Veritabanı başarıyla oluşturuldu!")
            return True
            
        except mysql.connector.Error as err:
            if attempt < max_retries - 1:
                print(f"Veritabanı hatası: {err}")
                print(f"{retry_delay} saniye sonra tekrar denenecek...")
                time.sleep(retry_delay)
            else:
                print(f"Veritabanı oluşturulamadı: {err}")
                raise err
        finally:
            close_db_connection(conn, cursor) 
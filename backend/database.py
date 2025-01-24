import mysql.connector
from datetime import datetime
import re
from config import db_config

def init_db():
    """Veritabanı oluşturur"""
    try:
        print("Veritabanına bağlanılıyor...")
        conn = mysql.connector.connect(
            host=db_config['host'],
            user=db_config['user'],
            password=db_config['password']
        )
        cursor = conn.cursor()
        
        print("Veritabanı oluşturuluyor...")
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_config['database']}")
        cursor.execute(f"USE {db_config['database']}")
        
        print("Tablolar oluşturuluyor...")
        # Bölümler tablosu
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bolumler (
                id INT AUTO_INCREMENT PRIMARY KEY,
                bolum_adi VARCHAR(100) NOT NULL,
                klasor_adi VARCHAR(100) NOT NULL,
                olusturma_tarihi DATETIME NOT NULL
            )
        """)
        
        # Dersler tablosu (bölüme bağlı)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS dersler (
                id INT AUTO_INCREMENT PRIMARY KEY,
                bolum_id INT NOT NULL,
                ders_adi VARCHAR(100) NOT NULL,
                klasor_adi VARCHAR(100) NOT NULL,
                olusturma_tarihi DATETIME NOT NULL,
                FOREIGN KEY (bolum_id) REFERENCES bolumler(id)
            )
        """)
        
        # Haftalar tablosu (derse bağlı)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS haftalar (
                id INT AUTO_INCREMENT PRIMARY KEY,
                ders_id INT NOT NULL,
                hafta_no INT NOT NULL,
                olusturma_tarihi DATETIME NOT NULL,
                FOREIGN KEY (ders_id) REFERENCES dersler(id)
            )
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
                FOREIGN KEY (hafta_id) REFERENCES haftalar(id)
            )
        """)
        
        conn.commit()
        cursor.close()
        conn.close()
        print("Veritabanı başarıyla oluşturuldu!")
        
    except mysql.connector.Error as err:
        print(f"Veritabanı hatası: {err}")
        raise err

def get_db_connection():
    """Veritabanı bağlantısı oluşturur"""
    try:
        conn = mysql.connector.connect(**db_config)
        return conn
    except mysql.connector.Error as err:
        print(f"Veritabanı bağlantı hatası: {err}")
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
        raise err 
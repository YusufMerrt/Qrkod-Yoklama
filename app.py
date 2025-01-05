from flask import Flask, render_template, request, redirect, url_for, jsonify
import qrcode
import base64
from io import BytesIO
import random
import string
import mysql.connector
from datetime import datetime
import re
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)

# IP sınırlandırması için Limiter yapılandırması
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day"]
)

# MySQL bağlantı bilgileri
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'ders_otomata'
}

def create_schema_for_course(cursor, ders_adi):
    """Ders için veritabanı oluşturur"""
    # Türkçe karakterleri ve boşlukları temizle
    schema_name = re.sub(r'[^a-zA-Z0-9]', '_', ders_adi.lower())
    
    # Veritabanı oluştur
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {schema_name}")
    return schema_name

def create_table_for_week(cursor, schema_name, hafta):
    """Hafta için tablo oluşturur"""
    cursor.execute(f"USE {schema_name}")
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS hafta_{hafta} (
            id INT AUTO_INCREMENT PRIMARY KEY,
            ad VARCHAR(50) NOT NULL,
            soyad VARCHAR(50) NOT NULL,
            ogrenci_no VARCHAR(11) NOT NULL,
            kayit_tarihi DATETIME NOT NULL,
            qr_kod_id VARCHAR(50) NOT NULL
        )
    """)
    return f"hafta_{hafta}"

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

def generate_random_string(length=10):
    """Rastgele bir string oluşturur"""
    letters = string.ascii_letters + string.digits
    return ''.join(random.choice(letters) for i in range(length))

def generate_qr_code(ders_id, hafta_no):
    """QR kod oluşturur ve base64 formatında döndürür"""
    timestamp = int(datetime.now().timestamp())  # QR kod oluşturma zamanı
    random_id = f"{generate_random_string()}_{timestamp}"  # QR kod ID'sine timestamp'i ekle
    base_url = request.host_url.rstrip('/')
    qr_url = f"{base_url}/form/{random_id}/{ders_id}/{hafta_no}/{timestamp}"
    
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(qr_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return img_str, timestamp

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/qr-generator')
def qr_generator():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        
        # Bölümleri getir
        cursor.execute("""
            SELECT b.*, 
                   (SELECT COUNT(DISTINCT d.id) 
                    FROM dersler d 
                    WHERE d.bolum_id = b.id) as ders_sayisi
            FROM bolumler b 
            ORDER BY b.bolum_adi
        """)
        bolumler = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return render_template('qr_generator.html', bolumler=bolumler)
        
    except mysql.connector.Error as err:
        print(f"Veritabanı hatası: {err}")
        return render_template('error.html', message=str(err))

@app.route('/get-dersler/<int:bolum_id>')
def get_dersler(bolum_id):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT dersler.*, 
                   (SELECT COUNT(DISTINCT h.id) 
                    FROM haftalar h 
                    WHERE h.ders_id = dersler.id) as hafta_sayisi
            FROM dersler 
            WHERE bolum_id = %s 
            ORDER BY ders_adi
        """, (bolum_id,))
        dersler = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify(dersler)
        
    except mysql.connector.Error as err:
        print(f"Veritabanı hatası: {err}")
        return jsonify({'error': str(err)})

@app.route('/get-haftalar/<int:ders_id>')
def get_haftalar(ders_id):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        
        # Mevcut haftaları al
        cursor.execute("""
            SELECT h.*, 
                   (SELECT COUNT(*) 
                    FROM yoklamalar y 
                    WHERE y.hafta_id = h.id) as kayit_sayisi
            FROM haftalar h 
            WHERE h.ders_id = %s 
            ORDER BY h.hafta_no
        """, (ders_id,))
        mevcut_haftalar = cursor.fetchall()
        
        # Mevcut hafta numaralarını al
        mevcut_hafta_nolari = [h['hafta_no'] for h in mevcut_haftalar]
        
        # 1'den 14'e kadar tüm haftaları oluştur
        tum_haftalar = []
        for i in range(1, 15):
            if i in mevcut_hafta_nolari:
                # Eğer hafta mevcutsa, veritabanından gelen bilgileri kullan
                hafta = next(h for h in mevcut_haftalar if h['hafta_no'] == i)
                tum_haftalar.append(hafta)
            else:
                # Eğer hafta mevcut değilse, yeni bir hafta oluştur
                tum_haftalar.append({
                    'hafta_no': i,
                    'kayit_sayisi': 0
                })
        
        cursor.close()
        conn.close()
        
        return jsonify(tum_haftalar)
        
    except mysql.connector.Error as err:
        print(f"Veritabanı hatası: {err}")
        return jsonify({'error': str(err)})

@app.route('/generate', methods=['GET', 'POST'])
def generate():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        
        if request.method == 'POST':
            bolum_id = request.form.get('bolum')
            ders_id = request.form.get('ders')
            hafta_no = request.form.get('hafta')
        else:
            ders_id = request.args.get('ders_id')
            hafta_no = request.args.get('hafta_no')
            
            if not ders_id or not hafta_no:
                return redirect(url_for('qr_generator'))
        
        # Ders bilgilerini al
        cursor.execute("""
            SELECT d.*, b.bolum_adi 
            FROM dersler d 
            JOIN bolumler b ON d.bolum_id = b.id 
            WHERE d.id = %s
        """, (ders_id,))
        ders = cursor.fetchone()
        
        if not ders:
            return render_template('error.html', message="Ders bulunamadı")
        
        # Hafta var mı kontrol et, yoksa oluştur
        cursor.execute("""
            SELECT * FROM haftalar 
            WHERE ders_id = %s AND hafta_no = %s
        """, (ders_id, hafta_no))
        hafta = cursor.fetchone()
        
        if not hafta:
            # Yeni hafta oluştur
            cursor.execute("""
                INSERT INTO haftalar (ders_id, hafta_no, olusturma_tarihi)
                VALUES (%s, %s, %s)
            """, (ders_id, hafta_no, datetime.now()))
            conn.commit()
            
            cursor.execute("""
                SELECT * FROM haftalar 
                WHERE ders_id = %s AND hafta_no = %s
            """, (ders_id, hafta_no))
            hafta = cursor.fetchone()
        
        qr_code, timestamp = generate_qr_code(ders_id, hafta_no)
        
        # Bölümleri tekrar getir
        cursor.execute("""
            SELECT b.*, 
                   (SELECT COUNT(DISTINCT d.id) 
                    FROM dersler d 
                    WHERE d.bolum_id = b.id) as ders_sayisi
            FROM bolumler b 
            ORDER BY b.bolum_adi
        """)
        bolumler = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return render_template('qr_generator.html', 
                             qr_code=qr_code,
                             ders_adi=f"{ders['bolum_adi']} - {ders['ders_adi']} - Hafta {hafta_no}",
                             bolumler=bolumler,
                             ders_id=ders_id,
                             hafta_no=hafta_no)
        
    except mysql.connector.Error as err:
        print(f"Veritabanı hatası: {err}")
        return render_template('error.html', message=str(err))

def get_bolumler():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM bolumler ORDER BY bolum_adi")
        bolumler = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return bolumler
        
    except mysql.connector.Error as err:
        print(f"Veritabanı hatası: {err}")
        return []

@app.route('/list-records')
def list_records():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        
        # Dersleri ve hafta bilgilerini getir
        cursor.execute("""
            SELECT d.*, b.bolum_adi,
                   (SELECT GROUP_CONCAT(h.id ORDER BY h.hafta_no)
                    FROM haftalar h 
                    WHERE h.ders_id = d.id) as hafta_idleri,
                   (SELECT GROUP_CONCAT(h.hafta_no ORDER BY h.hafta_no)
                    FROM haftalar h 
                    WHERE h.ders_id = d.id) as hafta_nolari
            FROM dersler d
            JOIN bolumler b ON d.bolum_id = b.id
            ORDER BY d.ders_adi
        """)
        dersler = cursor.fetchall()
        
        # Her ders için hafta bilgilerini düzenle
        ders_verileri = []
        for ders in dersler:
            if ders['hafta_nolari'] and ders['hafta_idleri']:
                hafta_nolari = [int(h) for h in ders['hafta_nolari'].split(',')]
                hafta_idleri = [int(h) for h in ders['hafta_idleri'].split(',')]
                
                # Her hafta için kayıt sayısını al
                hafta_verileri = []
                for hafta_no, hafta_id in zip(hafta_nolari, hafta_idleri):
                    cursor.execute("""
                        SELECT COUNT(*) as kayit_sayisi 
                        FROM yoklamalar y
                        WHERE y.hafta_id = %s
                    """, (hafta_id,))
                    kayit_sayisi = cursor.fetchone()['kayit_sayisi']
                    
                    if kayit_sayisi > 0:  # Sadece kayıt olan haftaları göster
                        hafta_verileri.append({
                            'hafta_no': hafta_no,
                            'kayit_sayisi': kayit_sayisi,
                            'hafta_id': hafta_id
                        })
                
                if hafta_verileri:  # Sadece kayıtlı haftası olan dersleri göster
                    ders_verileri.append({
                        'ders_adi': f"{ders['bolum_adi']} - {ders['ders_adi']}",
                        'id': ders['id'],
                        'haftalar': hafta_verileri
                    })
        
        cursor.close()
        conn.close()
        
        return render_template('records.html', dersler=ders_verileri)
        
    except mysql.connector.Error as err:
        print(f"Veritabanı hatası: {err}")
        return render_template('records.html', error=str(err))

@app.route('/view-records/<int:ders_id>/<int:hafta_id>')
def view_records(ders_id, hafta_id):
    try:
        # Ders bilgilerini al
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT ders_adi FROM dersler WHERE id = %s", (ders_id,))
        ders = cursor.fetchone()
        
        if not ders:
            return "Ders bulunamadı", 404
            
        # Hafta kayıtlarını al
        cursor.execute("""
            SELECT ad, soyad, ogrenci_no, DATE_FORMAT(kayit_zamani, '%d.%m.%Y %H:%i:%s') as kayit_zamani, 
            TIMESTAMPDIFF(SECOND, qr_olusturma_zamani, kayit_zamani) as kayit_suresi
            FROM hafta_{ders_id}_{hafta_id}
            ORDER BY kayit_zamani DESC
        """.format(ders_id=ders_id, hafta_id=hafta_id))
        
        kayitlar = cursor.fetchall()
        cursor.close()
        
        return render_template('view_records.html', 
                             ders_adi=ders['ders_adi'],
                             hafta_no=hafta_id,
                             kayitlar=kayitlar)
                             
    except Exception as e:
        return str(e), 500

@app.route('/form/<random_id>/<int:ders_id>/<int:hafta_no>/<int:olusturma_zamani>')
def form(random_id, ders_id, hafta_no, olusturma_zamani):
    try:
        # QR kodun geçerlilik süresini kontrol et (30 saniye)
        gecen_sure = int(datetime.now().timestamp()) - olusturma_zamani
        if gecen_sure > 30:
            return render_template('error.html', message="Bu QR kod süresi dolmuş. Lütfen yeni bir QR kod okutun.")
        
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        
        # Ders bilgilerini al
        cursor.execute("""
            SELECT d.*, b.bolum_adi 
            FROM dersler d 
            JOIN bolumler b ON d.bolum_id = b.id 
            WHERE d.id = %s
        """, (ders_id,))
        ders = cursor.fetchone()
        
        if not ders:
            return render_template('error.html', message="Ders bulunamadı")
        
        # Hafta bilgilerini al
        cursor.execute("""
            SELECT * FROM haftalar 
            WHERE ders_id = %s AND hafta_no = %s
        """, (ders_id, hafta_no))
        hafta = cursor.fetchone()
        
        if not hafta:
            return render_template('error.html', message="Hafta bulunamadı")
        
        cursor.close()
        conn.close()
        
        return render_template('form.html', 
                             ders=ders,
                             hafta=hafta,
                             qr_kod_id=random_id,
                             olusturma_zamani=olusturma_zamani)
        
    except mysql.connector.Error as err:
        print(f"Veritabanı hatası: {err}")
        return render_template('error.html', message=str(err))

@app.route('/submit_form', methods=['POST'])
@limiter.limit("1 per 45 minutes")  # Her IP için 45 dakikada bir form gönderme sınırı
def submit_form():
    name = request.form.get('name')
    surname = request.form.get('surname')
    student_id = request.form.get('student_id')
    ders_id = request.form.get('ders_id')
    hafta_id = request.form.get('hafta_id')
    qr_kod_id = request.form.get('qr_kod_id')
    olusturma_zamani = int(request.form.get('olusturma_zamani'))
    
    try:
        # QR kodun geçerlilik süresini kontrol et (30 saniye)
        gecen_sure = int(datetime.now().timestamp()) - olusturma_zamani
        if gecen_sure > 30:
            return render_template('error.html', message="Bu QR kod süresi dolmuş. Lütfen yeni bir QR kod okutun.")
        
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        
        # Önce aynı öğrencinin aynı QR kod ile kaydının olup olmadığını kontrol et
        cursor.execute("""
            SELECT COUNT(*) as count FROM yoklamalar 
            WHERE hafta_id = %s AND ogrenci_no = %s AND qr_kod_id = %s
        """, (hafta_id, student_id, qr_kod_id))
        count = cursor.fetchone()['count']
        
        if count == 0:  # Eğer kayıt yoksa ekle
            kayit_zamani = datetime.now()
            cursor.execute("""
                INSERT INTO yoklamalar (hafta_id, ad, soyad, ogrenci_no, kayit_tarihi, qr_kod_id)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (hafta_id, name, surname, student_id, kayit_zamani, qr_kod_id))
            conn.commit()
            
            # Ders ve hafta bilgilerini al
            cursor.execute("""
                SELECT d.ders_adi, b.bolum_adi, h.hafta_no
                FROM dersler d 
                JOIN bolumler b ON d.bolum_id = b.id
                JOIN haftalar h ON h.ders_id = d.id
                WHERE h.id = %s
            """, (hafta_id,))
            ders_bilgisi = cursor.fetchone()
            
            if not ders_bilgisi:
                return render_template('error.html', message="Ders bilgisi bulunamadı")
            
            cursor.close()
            conn.close()
            
            return render_template('success.html',
                                name=name,
                                surname=surname,
                                student_id=student_id,
                                bolum_adi=ders_bilgisi['bolum_adi'],
                                ders_adi=ders_bilgisi['ders_adi'],
                                hafta_no=ders_bilgisi['hafta_no'],
                                gecen_sure=gecen_sure)
        else:
            cursor.close()
            conn.close()
            return render_template('error.html',
                                message="Bu QR kod ile daha önce kayıt yapılmış. Lütfen yeni bir QR kod kullanın.")
            
    except mysql.connector.Error as err:
        print(f"Veritabanı hatası: {err}")
        return render_template('error.html', message=str(err))

@app.route('/bolumler')
def list_bolumler():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM bolumler ORDER BY bolum_adi")
        bolumler = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return render_template('bolumler.html', bolumler=bolumler)
        
    except mysql.connector.Error as err:
        print(f"Veritabanı hatası: {err}")
        return render_template('error.html', message=str(err))

@app.route('/bolum/<int:bolum_id>/dersler')
def list_dersler(bolum_id):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        
        # Bölüm bilgisini al
        cursor.execute("SELECT * FROM bolumler WHERE id = %s", (bolum_id,))
        bolum = cursor.fetchone()
        
        # Bölüme ait dersleri al
        cursor.execute("""
            SELECT d.*, 
                   (SELECT COUNT(DISTINCT h.id) 
                    FROM haftalar h 
                    WHERE h.ders_id = d.id) as hafta_sayisi
            FROM dersler d 
            WHERE d.bolum_id = %s 
            ORDER BY d.ders_adi
        """, (bolum_id,))
        dersler = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return render_template('dersler.html', bolum=bolum, dersler=dersler)
        
    except mysql.connector.Error as err:
        print(f"Veritabanı hatası: {err}")
        return render_template('error.html', message=str(err))

@app.route('/ders/<int:ders_id>/haftalar')
def list_haftalar(ders_id):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        
        # Ders bilgisini al
        cursor.execute("""
            SELECT d.*, b.bolum_adi 
            FROM dersler d 
            JOIN bolumler b ON d.bolum_id = b.id 
            WHERE d.id = %s
        """, (ders_id,))
        ders = cursor.fetchone()
        
        # Derse ait haftaları al
        cursor.execute("""
            SELECT h.*, 
                   (SELECT COUNT(*) 
                    FROM yoklamalar y 
                    WHERE y.hafta_id = h.id) as kayit_sayisi
            FROM haftalar h 
            WHERE h.ders_id = %s 
            ORDER BY h.hafta_no
        """, (ders_id,))
        haftalar = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return render_template('haftalar.html', ders=ders, haftalar=haftalar)
        
    except mysql.connector.Error as err:
        print(f"Veritabanı hatası: {err}")
        return render_template('error.html', message=str(err))

@app.route('/bolum/ekle', methods=['GET', 'POST'])
def bolum_ekle():
    if request.method == 'POST':
        bolum_adi = request.form.get('bolum_adi')
        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO bolumler (bolum_adi, olusturma_tarihi)
                VALUES (%s, %s)
            """, (bolum_adi, datetime.now()))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            return redirect(url_for('list_bolumler'))
            
        except mysql.connector.Error as err:
            print(f"Veritabanı hatası: {err}")
            return render_template('error.html', message=str(err))
            
    return render_template('bolum_ekle.html')

@app.route('/ders/ekle/<int:bolum_id>', methods=['GET', 'POST'])
def ders_ekle(bolum_id):
    if request.method == 'POST':
        ders_adi = request.form.get('ders_adi')
        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO dersler (bolum_id, ders_adi, olusturma_tarihi)
                VALUES (%s, %s, %s)
            """, (bolum_id, ders_adi, datetime.now()))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            return redirect(url_for('list_dersler', bolum_id=bolum_id))
            
        except mysql.connector.Error as err:
            print(f"Veritabanı hatası: {err}")
            return render_template('error.html', message=str(err))
            
    return render_template('ders_ekle.html', bolum_id=bolum_id)

@app.route('/hafta/ekle/<int:ders_id>', methods=['GET', 'POST'])
def hafta_ekle(ders_id):
    if request.method == 'POST':
        hafta_no = request.form.get('hafta_no')
        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO haftalar (ders_id, hafta_no, olusturma_tarihi)
                VALUES (%s, %s, %s)
            """, (ders_id, hafta_no, datetime.now()))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            return redirect(url_for('list_haftalar', ders_id=ders_id))
            
        except mysql.connector.Error as err:
            print(f"Veritabanı hatası: {err}")
            return render_template('error.html', message=str(err))
            
    return render_template('hafta_ekle.html', ders_id=ders_id)

@app.route('/kayitlar')
def kayitlar():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        
        # Filtreleri al
        bolum_id = request.args.get('bolum', type=int)
        ders_id = request.args.get('ders', type=int)
        hafta_no = request.args.get('hafta', type=int)
        page = request.args.get('page', 1, type=int)
        per_page = 10  # Sayfa başına kayıt sayısı

        # Temel sorgu
        query = """
            SELECT y.ogrenci_no, CONCAT(y.ad, ' ', y.soyad) as ad_soyad,
                   b.bolum_adi, d.ders_adi, h.hafta_no as hafta,
                   DATE_FORMAT(y.kayit_tarihi, '%d.%m.%Y %H:%i') as tarih,
                   1 as durum
            FROM yoklamalar y
            JOIN haftalar h ON y.hafta_id = h.id
            JOIN dersler d ON h.ders_id = d.id
            JOIN bolumler b ON d.bolum_id = b.id
            WHERE 1=1
        """
        params = []

        # Filtreleri uygula
        if bolum_id:
            query += " AND b.id = %s"
            params.append(bolum_id)
        if ders_id:
            query += " AND d.id = %s"
            params.append(ders_id)
        if hafta_no:
            query += " AND h.hafta_no = %s"
            params.append(hafta_no)

        # Toplam kayıt sayısını al
        count_query = f"SELECT COUNT(*) as total FROM ({query}) as count_table"
        cursor.execute(count_query, params)
        total_records = cursor.fetchone()['total']
        total_pages = (total_records + per_page - 1) // per_page

        # Sayfalama için LIMIT ve OFFSET ekle
        query += " ORDER BY y.kayit_tarihi DESC LIMIT %s OFFSET %s"
        params.extend([per_page, (page - 1) * per_page])

        # Kayıtları al
        cursor.execute(query, params)
        kayitlar = cursor.fetchall()

        # Bölümleri al
        cursor.execute("""
            SELECT b.*, 
                   (SELECT COUNT(*) FROM dersler WHERE bolum_id = b.id) as ders_sayisi 
            FROM bolumler b
        """)
        bolumler = cursor.fetchall()

        cursor.close()
        conn.close()

        return render_template('view_records.html',
                             kayitlar=kayitlar,
                             bolumler=bolumler,
                             current_page=page,
                             total_pages=total_pages)

    except mysql.connector.Error as err:
        print(f"Veritabanı hatası: {err}")
        return render_template('error.html', message=str(err))

if __name__ == '__main__':
    init_db()  # Uygulama başlatılırken veritabanını oluştur
    app.run(debug=True, host='0.0.0.0') 
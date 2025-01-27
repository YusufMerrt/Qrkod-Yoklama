from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from datetime import datetime
import re

from config import Config, db_config
from database import init_db, get_db_connection, close_db_connection
from qr_utils import generate_qr_code

app = Flask(__name__, 
           template_folder=Config.TEMPLATES_FOLDER,
           static_folder=Config.STATIC_FOLDER)
app.config.from_object(Config)

# IP sınırlandırması için Limiter yapılandırması
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=[Config.RATELIMIT_DEFAULT]
)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/bolumler')
def list_bolumler():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT b.*, 
                   (SELECT COUNT(DISTINCT d.id) 
                    FROM dersler d 
                    WHERE d.bolum_id = b.id) as ders_sayisi
            FROM bolumler b 
            ORDER BY b.bolum_adi
        """)
        bolumler = cursor.fetchall()
        
        close_db_connection(conn, cursor)
        return render_template('bolumler.html', bolumler=bolumler)
        
    except Exception as err:
        return render_template('error.html', error=str(err))

@app.route('/bolum/ekle', methods=['GET', 'POST'])
def bolum_ekle():
    if request.method == 'POST':
        bolum_adi = request.form.get('bolum_adi')
        if not bolum_adi:
            return render_template('bolum_ekle.html', error="Bölüm adı boş olamaz")
            
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Klasör adını oluştur (türkçe karakterleri ve boşlukları temizle)
            klasor_adi = re.sub(r'[^a-zA-Z0-9]', '_', bolum_adi.lower())
            
            cursor.execute("""
                INSERT INTO bolumler (bolum_adi, klasor_adi, olusturma_tarihi)
                VALUES (%s, %s, %s)
            """, (bolum_adi, klasor_adi, datetime.now()))
            
            conn.commit()
            close_db_connection(conn, cursor)
            
            return redirect(url_for('list_bolumler'))
            
        except Exception as err:
            return render_template('bolum_ekle.html', error=str(err))
            
    return render_template('bolum_ekle.html')

@app.route('/bolum/<int:bolum_id>/dersler')
def list_dersler(bolum_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Bölüm bilgisini al
        cursor.execute("""
            SELECT * FROM bolumler WHERE id = %s
        """, (bolum_id,))
        bolum = cursor.fetchone()
        
        if not bolum:
            return render_template('error.html', error="Bölüm bulunamadı")
        
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
        
        close_db_connection(conn, cursor)
        return render_template('dersler.html', bolum=bolum, dersler=dersler)
        
    except Exception as err:
        return render_template('error.html', error=str(err))

@app.route('/ders/ekle/<int:bolum_id>', methods=['GET', 'POST'])
def ders_ekle(bolum_id):
    if request.method == 'POST':
        ders_adi = request.form.get('ders_adi')
        if not ders_adi:
            return render_template('ders_ekle.html', error="Ders adı boş olamaz", bolum_id=bolum_id)
            
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Klasör adını oluştur
            klasor_adi = re.sub(r'[^a-zA-Z0-9]', '_', ders_adi.lower())
            
            cursor.execute("""
                INSERT INTO dersler (bolum_id, ders_adi, klasor_adi, olusturma_tarihi)
                VALUES (%s, %s, %s, %s)
            """, (bolum_id, ders_adi, klasor_adi, datetime.now()))
            
            conn.commit()
            close_db_connection(conn, cursor)
            
            return redirect(url_for('list_dersler', bolum_id=bolum_id))
            
        except Exception as err:
            return render_template('ders_ekle.html', error=str(err), bolum_id=bolum_id)
            
    return render_template('ders_ekle.html', bolum_id=bolum_id)

@app.route('/kayitlar')
def list_kayitlar():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Filtreleri al
        bolum_id = request.args.get('bolum', type=int)
        ders_id = request.args.get('ders', type=int)
        hafta_no = request.args.get('hafta', type=int)
        page = request.args.get('page', 1, type=int)
        per_page = 10  # Sayfa başına kayıt sayısı
        
        # Temel sorgu
        query = """
            SELECT y.*, h.hafta_no, d.ders_adi, b.bolum_adi,
                   DATE_FORMAT(y.kayit_tarihi, '%d.%m.%Y %H:%i') as kayit_tarihi_str
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
        cursor.execute(count_query, tuple(params))
        total_records = cursor.fetchone()['total']
        total_pages = (total_records + per_page - 1) // per_page
        
        # Sayfalama için LIMIT ve OFFSET ekle
        query += " ORDER BY y.kayit_tarihi DESC LIMIT %s OFFSET %s"
        params.extend([per_page, (page - 1) * per_page])
        
        # Kayıtları al
        cursor.execute(query, tuple(params))
        kayitlar = cursor.fetchall()
        
        # Bölümleri al (filtre için)
        cursor.execute("""
            SELECT b.*, 
                   (SELECT COUNT(DISTINCT d.id) 
                    FROM dersler d 
                    WHERE d.bolum_id = b.id) as ders_sayisi
            FROM bolumler b
            ORDER BY b.bolum_adi
        """)
        bolumler = cursor.fetchall()
        
        close_db_connection(conn, cursor)
        
        return render_template('kayitlar.html',
                             kayitlar=kayitlar,
                             bolumler=bolumler,
                             current_page=page,
                             total_pages=total_pages,
                             selected_bolum=bolum_id,
                             selected_ders=ders_id,
                             selected_hafta=hafta_no)
                             
    except Exception as err:
        return render_template('error.html', error=str(err))

@app.route('/qr-generator')
def qr_generator():
    try:
        conn = get_db_connection()
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
        
        close_db_connection(conn, cursor)
        return render_template('qr_generator.html', bolumler=bolumler)
        
    except Exception as err:
        return render_template('error.html', error=str(err))

@app.route('/generate', methods=['GET', 'POST'])
def generate():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        if request.method == 'POST':
            ders_id = request.form.get('ders')
            hafta_no = request.form.get('hafta')
            # POST isteği geldiğinde, QR kod oluşturduktan sonra GET parametreleriyle yönlendir
            if ders_id and hafta_no:
                return redirect(url_for('generate', ders_id=ders_id, hafta_no=hafta_no))
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
            return render_template('error.html', error="Ders bulunamadı")
        
        # Hafta var mı kontrol et, yoksa oluştur
        cursor.execute("""
            SELECT * FROM haftalar 
            WHERE ders_id = %s AND hafta_no = %s
        """, (ders_id, hafta_no))
        hafta = cursor.fetchone()
        
        if not hafta:
            cursor.execute("""
                INSERT INTO haftalar (ders_id, hafta_no, olusturma_tarihi)
                VALUES (%s, %s, %s)
            """, (ders_id, hafta_no, datetime.now()))
            conn.commit()
            
        base_url = request.host_url.rstrip('/')
        qr_code, timestamp, _ = generate_qr_code(base_url, ders_id, hafta_no)
        
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
        
        close_db_connection(conn, cursor)
        
        return render_template('qr_generator.html', 
                             qr_code=qr_code,
                             bolum_adi=ders['bolum_adi'],
                             ders_adi=ders['ders_adi'],
                             hafta_no=hafta_no,
                             tarih=datetime.now().strftime('%d.%m.%Y %H:%M'),
                             bolumler=bolumler)
                             
    except Exception as err:
        return render_template('error.html', error=str(err))

@app.route('/yoklama/<random_id>/<int:ders_id>/<int:hafta_no>/<int:olusturma_zamani>')
def yoklama_form(random_id, ders_id, hafta_no, olusturma_zamani):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Ders ve bölüm bilgilerini al
        cursor.execute("""
            SELECT d.id, d.ders_adi, b.bolum_adi
            FROM dersler d
            JOIN bolumler b ON d.bolum_id = b.id
            WHERE d.id = %s
        """, (ders_id,))
        ders_bilgisi = cursor.fetchone()
        
        if not ders_bilgisi:
            return render_template('error.html', error="Ders bulunamadı.")
        
        close_db_connection(conn, cursor)
        
        return render_template('form.html', 
                             ders=ders_bilgisi,
                             hafta_no=hafta_no,
                             qr_kod_id=random_id,
                             olusturma_zamani=olusturma_zamani)
                             
    except Exception as err:
        return render_template('error.html', error=str(err))

@app.route('/submit_form', methods=['POST'])
def submit_form():
    try:
        # Form verilerini al
        ad = request.form.get('name', '').strip()
        soyad = request.form.get('surname', '').strip()
        ogrenci_no = request.form.get('student_id', '').strip()
        ders_id = request.form.get('ders_id')
        hafta_no = request.form.get('hafta_no')
        qr_kod_id = request.form.get('qr_kod_id')
        olusturma_zamani = request.form.get('olusturma_zamani')
        
        # Verileri doğrula
        if not all([ad, soyad, ogrenci_no, ders_id, hafta_no, qr_kod_id, olusturma_zamani]):
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT d.ders_adi, b.bolum_adi
                FROM dersler d
                JOIN bolumler b ON d.bolum_id = b.id
                WHERE d.id = %s
            """, (ders_id,))
            ders_bilgisi = cursor.fetchone()
            close_db_connection(conn, cursor)
            
            return render_template('form.html', 
                                error="Lütfen tüm alanları doldurun.",
                                ders=ders_bilgisi,
                                hafta_no=hafta_no,
                                qr_kod_id=qr_kod_id,
                                olusturma_zamani=olusturma_zamani)
        
        # Öğrenci numarası formatını kontrol et
        if not re.match(r'^\d{11}$', ogrenci_no):
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT d.ders_adi, b.bolum_adi
                FROM dersler d
                JOIN bolumler b ON d.bolum_id = b.id
                WHERE d.id = %s
            """, (ders_id,))
            ders_bilgisi = cursor.fetchone()
            close_db_connection(conn, cursor)
            
            return render_template('form.html', 
                                error="Öğrenci numarası 11 haneli olmalıdır.",
                                ders=ders_bilgisi,
                                hafta_no=hafta_no,
                                qr_kod_id=qr_kod_id,
                                olusturma_zamani=olusturma_zamani)
        
        # QR kodun geçerliliğini kontrol et
        current_time = int(datetime.now().timestamp())
        qr_olusturma_zamani = int(olusturma_zamani)
        if current_time - qr_olusturma_zamani > 60:  # 60 saniye geçerlilik süresi
            return render_template('error.html', error="QR kod süresi dolmuş. Lütfen yeni bir QR kod okutun.")
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Aynı öğrencinin aynı hafta için daha önce yoklama kaydı var mı kontrol et
        cursor.execute("""
            SELECT y.* FROM yoklamalar y
            JOIN haftalar h ON y.hafta_id = h.id
            WHERE h.ders_id = %s AND h.hafta_no = %s AND y.ogrenci_no = %s
        """, (ders_id, hafta_no, ogrenci_no))
        
        existing_record = cursor.fetchone()
        if existing_record:
            close_db_connection(conn, cursor)
            return render_template('error.html', error="Bu ders ve hafta için zaten yoklama kaydınız bulunmaktadır.")
        
        # Rate limit kontrolü - sadece başarılı kayıtlar için
        try:
            limiter.check("1 per 45 minutes")
        except:
            close_db_connection(conn, cursor)
            return render_template('error.html', error="Çok fazla yoklama kaydı girdiniz. Lütfen 45 dakika bekleyin.")
        
        # Hafta ID'sini bul veya oluştur
        cursor.execute("""
            SELECT id FROM haftalar 
            WHERE ders_id = %s AND hafta_no = %s
        """, (ders_id, hafta_no))
        hafta = cursor.fetchone()
        
        if not hafta:
            cursor.execute("""
                INSERT INTO haftalar (ders_id, hafta_no, olusturma_tarihi)
                VALUES (%s, %s, NOW())
            """, (ders_id, hafta_no))
            conn.commit()
            hafta_id = cursor.lastrowid
        else:
            hafta_id = hafta['id']
        
        # Yoklama kaydını ekle
        cursor.execute("""
            INSERT INTO yoklamalar (hafta_id, ad, soyad, ogrenci_no, kayit_tarihi, qr_kod_id)
            VALUES (%s, %s, %s, %s, NOW(), %s)
        """, (hafta_id, ad, soyad, ogrenci_no, qr_kod_id))
        conn.commit()
        
        # Ders bilgilerini al
        cursor.execute("""
            SELECT d.ders_adi, b.bolum_adi
            FROM dersler d
            JOIN bolumler b ON d.bolum_id = b.id
            WHERE d.id = %s
        """, (ders_id,))
        ders_bilgisi = cursor.fetchone()
        
        close_db_connection(conn, cursor)
        
        return render_template('success.html',
                             name=ad,
                             surname=soyad,
                             student_id=ogrenci_no,
                             ders_adi=ders_bilgisi['ders_adi'],
                             bolum_adi=ders_bilgisi['bolum_adi'],
                             hafta_no=hafta_no,
                             tarih=datetime.now().strftime('%d.%m.%Y %H:%M'),
                             message="Yoklamanız başarıyla kaydedildi.")
                             
    except Exception as err:
        return render_template('form.html', 
                            error=str(err),
                            ders=request.form,
                            hafta_no=hafta_no,
                            qr_kod_id=qr_kod_id,
                            olusturma_zamani=olusturma_zamani)

@app.route('/get-dersler/<int:bolum_id>')
def get_dersler(bolum_id):
    try:
        conn = get_db_connection()
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
        
        close_db_connection(conn, cursor)
        return jsonify(dersler)
        
    except Exception as err:
        return jsonify({'error': str(err)})

@app.route('/get-haftalar/<int:ders_id>')
def get_haftalar(ders_id):
    try:
        conn = get_db_connection()
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
        
        close_db_connection(conn, cursor)
        return jsonify(tum_haftalar)
        
    except Exception as err:
        return jsonify({'error': str(err)})

if __name__ == '__main__':
    init_db()  # Uygulama başlatılırken veritabanını oluştur
    app.run(debug=Config.DEBUG, host='0.0.0.0') 
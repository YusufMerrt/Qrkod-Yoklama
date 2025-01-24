# QR Kod Yoklama Sistemi

Bu proje, üniversite derslerinde yoklama almak için QR kod tabanlı bir sistemdir.

## Özellikler

- Bölüm ve ders yönetimi
- QR kod oluşturma
- Yoklama alma ve kayıt
- Kayıt filtreleme ve raporlama
- Responsive tasarım

## Kurulum

1. Projeyi klonlayın:
```bash
git clone https://github.com/YusufMerrt/Qrkod-Yoklama.git
cd Qrkod-Yoklama
```

2. Gerekli paketleri yükleyin:
```bash
pip install -r requirements.txt
```

3. MySQL veritabanını kurun ve ayarları yapılandırın:
- MySQL Server'ı yükleyin
- `backend/config.py` dosyasındaki veritabanı ayarlarını düzenleyin

4. Uygulamayı başlatın:
```bash
cd backend
python app.py
```

5. Tarayıcıda açın:
```
http://localhost:5000
```

## Kullanım

1. Ana sayfadan "Bölüm ve Ders Yönetimi" seçeneğine tıklayın
2. Bölüm ve ders ekleyin
3. "QR Kod Oluştur" seçeneğiyle yoklama için QR kod oluşturun
4. Öğrenciler QR kodu okutarak yoklamaya katılabilir
5. "Kayıtları Görüntüle" seçeneğinden yoklama kayıtlarını görüntüleyin

## Gereksinimler

- Python 3.8+
- MySQL 5.7+
- Flask
- Flask-Limiter
- mysql-connector-python
- qrcode
- Pillow

## Lisans

Bu proje MIT lisansı altında lisanslanmıştır. Detaylar için [LICENSE](LICENSE) dosyasına bakın. 
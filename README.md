# QR Kod Yoklama Sistemi

Bu proje, üniversite derslerinde yoklama işlemlerini kolaylaştırmak ve dijitalleştirmek için geliştirilmiş QR kod tabanlı bir sistemdir.

## Sistem Hakkında

QR Kod Yoklama Sistemi, üniversitelerde derslerin yoklama sürecini hızlandırmak ve güvenilir hale getirmek için tasarlanmıştır. Sistem sayesinde:
- Kağıt israfının önüne geçilir
- Yoklama süresi kısalır
- Sahte yoklamaların önüne geçilir
- Yoklama kayıtları dijital ortamda güvenle saklanır

🌐 **Çalışır Sürüm**
Uygulamanın çalışır sürümüne [https://qrkod-yoklama.onrender.com](https://qrkod-yoklama.onrender.com) adresinden erişebilir ve hemen kullanmaya başlayabilirsiniz.

## Nasıl Kullanılır?

### Öğretim Görevlisi İçin:

1. **Bölüm ve Ders Yönetimi**
   - Sisteme yeni bölümler ekleyebilirsiniz
   - Her bölüm için dersler tanımlayabilirsiniz
   - Mevcut bölüm ve dersleri düzenleyebilirsiniz

2. **Yoklama Alma**
   - İlgili ders için QR kod oluşturun
   - Oluşturulan QR kodu öğrencilerle paylaşın
   - Yoklama süresini belirleyin
   - Canlı olarak yoklamaya katılımı takip edin

3. **Kayıt Görüntüleme**
   - Tüm yoklama kayıtlarını görüntüleyin
   - Tarihe göre filtreleme yapın
   - Derse göre filtreleme yapın
   - Yoklama raporları oluşturun

### Öğrenciler İçin:

1. QR kodu telefonunuzla tarayın
2. Açılan sayfada bilgilerinizi girin
3. Yoklamanızı onaylayın

## Özellikler

- ✨ Kolay kullanım
- 📱 Mobil uyumlu tasarım
- 🔒 Güvenli yoklama sistemi
- 📊 Detaylı raporlama
- 🎯 Anlık takip
- 📂 Dijital kayıt arşivi

## Gereksinimler

- Akıllı telefon (QR kod okuyucu)
- İnternet bağlantısı
- Web tarayıcısı

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

## Lisans

Bu proje MIT lisansı altında lisanslanmıştır. Detaylar için [LICENSE](LICENSE) dosyasına bakın. 
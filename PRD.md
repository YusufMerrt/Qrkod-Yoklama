# QR Kod Yoklama Sistemi - Ürün Gereksinim Dokümanı (PRD)

## 1. Ürün Vizyonu
QR Kod Yoklama Sistemi, üniversitelerde yoklama sürecini dijitalleştirerek zaman kaybını önlemeyi, güvenilirliği artırmayı ve kağıt israfını azaltmayı hedefleyen modern bir çözümdür.

## 2. Hedef Kitle
- **Birincil Kullanıcılar:** 
  - Üniversite öğretim görevlileri
  - Üniversite öğrencileri
- **İkincil Kullanıcılar:**
  - Bölüm başkanları
  - Fakülte yönetimi
  - İdari personel

## 3. Temel Özellikler

### 3.1 Bölüm ve Ders Yönetimi
- Bölüm ekleme, düzenleme ve silme
- Ders ekleme, düzenleme ve silme
- Dersleri bölümlerle ilişkilendirme
- Haftalık ders programı oluşturma

### 3.2 QR Kod Yönetimi
- Dinamik QR kod oluşturma
- Zaman sınırlı QR kodlar
- Tek kullanımlık QR kodlar
- QR kod geçerlilik süresi belirleme

### 3.3 Yoklama İşlemleri
- QR kod ile hızlı yoklama alma
- Öğrenci bilgilerini doğrulama
- Yoklama durumunu gerçek zamanlı görüntüleme
- Manuel yoklama düzenleme imkanı

### 3.4 Raporlama ve Analiz
- Ders bazlı yoklama raporları
- Öğrenci bazlı devam durumu
- Tarih aralığına göre filtreleme
- Excel/PDF formatında rapor çıktısı

## 4. Teknik Gereksinimler

### 4.1 Sistem Gereksinimleri
- Web tabanlı uygulama
- Responsive tasarım
- Tarayıcı uyumluluğu (Chrome, Firefox, Safari)
- Mobil cihaz desteği

### 4.2 Güvenlik Gereksinimleri
- Kullanıcı kimlik doğrulama
- Rol bazlı yetkilendirme
- QR kod şifreleme
- Veri yedekleme
- KVKK uyumluluğu

### 4.3 Performans Gereksinimleri
- Sayfa yüklenme süresi < 3 saniye
- QR kod okuma süresi < 2 saniye
- Eşzamanlı 1000+ kullanıcı desteği
- %99.9 uptime garantisi

## 5. Kullanıcı Arayüzü

### 5.1 Öğretim Görevlisi Paneli
- Dashboard görünümü
- Ders yönetim arayüzü
- QR kod oluşturma ekranı
- Raporlama ekranı

### 5.2 Öğrenci Arayüzü
- QR kod okuma sayfası
- Yoklama onay ekranı
- Devam durumu görüntüleme

## 6. Entegrasyonlar
- Üniversite öğrenci bilgi sistemi
- E-posta sistemi
- Google/Apple takvim

## 7. Veri Yönetimi
- MySQL veritabanı
- Düzenli yedekleme
- Veri saklama politikaları
- Veri temizleme kuralları

## 8. Yasal Gereksinimler
- KVKK uyumluluğu
- Aydınlatma metni
- Kullanıcı sözleşmesi
- Gizlilik politikası

## 9. Gelecek Geliştirmeler
- Bluetooth beacon desteği
- Yüz tanıma sistemi
- Mobil uygulama
- API servisleri
- Çoklu dil desteği

## 10. Başarı Kriterleri
- Yoklama süresinde %70 azalma
- Kağıt tüketiminde %90 azalma
- Kullanıcı memnuniyeti > %85
- Sistem kullanım oranı > %90 
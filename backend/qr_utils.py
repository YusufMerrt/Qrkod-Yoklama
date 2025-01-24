import qrcode
import base64
from io import BytesIO
import random
import string
from datetime import datetime

def generate_random_string(length=10):
    """Rastgele bir string oluşturur"""
    letters = string.ascii_letters + string.digits
    return ''.join(random.choice(letters) for i in range(length))

def generate_qr_code(base_url, ders_id, hafta_no):
    """QR kod oluşturur ve base64 formatında döndürür"""
    timestamp = int(datetime.now().timestamp())  # QR kod oluşturma zamanı
    random_id = f"{generate_random_string()}_{timestamp}"  # QR kod ID'sine timestamp'i ekle
    qr_url = f"{base_url}/yoklama/{random_id}/{ders_id}/{hafta_no}/{timestamp}"
    
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(qr_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return img_str, timestamp, random_id 
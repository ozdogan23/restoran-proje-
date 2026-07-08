from flask import Flask
import os
import psycopg2
from admin import admin_bp  # admin.py'yi bağlıyoruz

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'pinar23_gizli_anahtar')

# Admin panelini ekliyoruz
app.register_blueprint(admin_bp)

# --- VERİTABANI BAĞLANTI FONKSİYONU ---
def veritabanina_baglan():
    url = os.environ.get('DATABASE_URL')
    if not url:
        raise Exception("DATABASE_URL ortam değişkeni bulunamadı!")
    return psycopg2.connect(url, sslmode='require')

# Kategoriler için kapak resimleri
RESIM_MAP = {
    "Ana Yemekler": "https://images.unsplash.com/photo-1544025162-d76694265947?w=600&auto=format&fit=crop",
    "Dondurmalar": "https://images.unsplash.com/photo-1563805042-7684c019e1cb?w=600&auto=format&fit=crop",
    "Kahveler": "https://images.unsplash.com/photo-1509042239860-f550ce710b93?w=600&auto=format&fit=crop",
    "Soğuk İçecekler": "https://images.unsplash.com/photo-1513558161293-cdaf765ed2fd?w=600&auto=format&fit=crop",
    "Sıcak İçecekler": "https://images.unsplash.com/photo-1544787219-7f47ccb76574?w=600&auto=format&fit=crop",
    "Tatlılar": "https://images.unsplash.com/photo-1551024601-bec78aea704b?w=600&auto=format&fit=crop"
}
VARSAYILAN_RESIM = "https://images.unsplash.com/photo-1498654896293-37aacf113fd9?w=600&auto=format&fit=crop"

# --- ANA SAYFA ---
@app.route('/')
def ana_sayfa():
    return """
    <html><head><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { font-family: 'Segoe UI', sans-serif; background: url('https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=1200&auto=format&fit=crop') center/cover; margin: 0; height: 100vh; }
        .overlay { background: rgba(0,0,0,0.85); height: 100%; display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center; padding: 20px; }
        .btn-menu { text-decoration: none; background: #e65100; color: white; padding: 18px 45px; border-radius: 8px; font-weight: bold; }
    </style></head>
    <body><div class="overlay"><h1 style="color:white">YENİDEN</h1><a href="/menu" class="btn-menu">Menüyü Keşfet</a></div></body></html>
    """

# --- MENÜ SAYFASI ---
@app.route('/menu')
def menu_getir():
    baglanti = veritabanina_baglan()
    cursor = baglanti.cursor()
    cursor.execute("SELECT DISTINCT k.kategori_adi FROM Urunler u INNER JOIN Kategoriler k ON u.kategori_id = k.kategori_id ORDER BY k.kategori_adi")
    kategoriler = cursor.fetchall()
    html = "<html><head><style>body{background:#121212; color:white; font-family:sans-serif; text-align:center; padding:20px;}</style></head><body><h1>Kategoriler</h1>"
    for kat in kategoriler:
        html += f"<a href='/kategori/{kat[0]}' style='display:block; padding:20px; margin:10px; background:#1a1a1a; color:white; text-decoration:none;'>{kat[0]}</a>"
    html += "</body></html>"
    cursor.close(); baglanti.close()
    return html

# --- KATEGORİ DETAY ---
@app.route('/kategori/<ad>')
def kategori_detay(ad):
    baglanti = veritabanina_baglan()
    cursor = baglanti.cursor()
    cursor.execute("SELECT u.urun_adi, u.fiyat FROM Urunler u INNER JOIN Kategoriler k ON u.kategori_id = k.kategori_id WHERE k.kategori_adi = %s", (ad,))
    urunler = cursor.fetchall()
    html = f"<html><head><style>body{{background:#121212; color:white; font-family:sans-serif; padding:20px;}}</style></head><body><h1>{ad}</h1>"
    for u in urunler:
        html += f"<p>{u[0]} - {u[1]} ₺</p>"
    html += "<br><a href='/menu' style='color:orange;'>Geri Dön</a></body></html>"
    cursor.close(); baglanti.close()
    return html

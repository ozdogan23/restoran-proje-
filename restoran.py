from flask import Flask
import os
import psycopg2
from admin import admin_bp

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'pinar23_gizli_anahtar')

# Admin panelini Blueprint olarak ekliyoruz
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
        body { font-family: 'Segoe UI', Tahoma, sans-serif; background: url('https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=1200&auto=format&fit=crop') center/cover no-repeat; margin: 0; height: 100vh; }
        .overlay { background: rgba(15, 15, 15, 0.85); height: 100%; display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center; padding: 20px; }
        .brand-logo { font-size: 48px; color: #ffffff; font-weight: 900; letter-spacing: 2px; margin-bottom: 15px; text-transform: uppercase; border-bottom: 3px solid #e65100; padding-bottom: 10px; }
        .subtitle { font-size: 18px; color: #dcdde1; margin-bottom: 40px; font-weight: 300; max-width: 400px; line-height: 1.6; }
        .btn-menu { text-decoration: none; background-color: #e65100; color: white; padding: 18px 45px; border-radius: 8px; font-size: 18px; font-weight: bold; transition: 0.3s; letter-spacing: 1px; text-transform: uppercase; }
        .btn-menu:hover { background-color: #ff6600; }
    </style></head>
    <body><div class="overlay">
        <div class="brand-logo">YENİDEN</div>
        <div class="subtitle">Özenle seçilmiş malzemeler, usta ellerden çıkan eşsiz tarifler. Gerçek lezzet deneyimine davetlisiniz.</div>
        <a href="/menu" class="btn-menu">Menüyü Keşfet</a>
    </div></body></html>"""

# --- MENÜ SAYFASI ---
@app.route('/menu')
def menu_getir():
    baglanti = veritabanina_baglan()
    cursor = baglanti.cursor()
    cursor.execute("SELECT DISTINCT Kategoriler.kategori_adi FROM Urunler INNER JOIN Kategoriler ON Urunler.kategori_id = Kategoriler.kategori_id ORDER BY Kategoriler.kategori_adi")
    kategoriler = cursor.fetchall()
    
    html = "<html><head><meta name='viewport' content='width=device-width, initial-scale=1.0'><style>body{font-family:'Segoe UI', Tahoma, sans-serif; background-color:#121212; color:#ffffff; max-width:600px; margin:auto; padding:0; padding-bottom:50px;} .header-bar{display:flex; align-items:center; justify-content:space-between; padding:18px 20px; background-color:#1a1a1a; position:sticky; top:0; z-index:1000; border-bottom:1px solid #333;} .container{padding:25px 15px;} .bölüm-başlığı{font-size:24px; color:#ffffff; margin:0 5px 25px 5px; font-weight:900; border-left:4px solid #e65100; padding-left:10px;} .kategori-kartı{position:relative; height:150px; border-radius:10px; overflow:hidden; background-size:cover; background-position:center; display:flex; align-items:center; justify-content:center; text-decoration:none; margin-bottom:20px; box-shadow:0 8px 20px rgba(0,0,0,0.5); border:1px solid #333;} .overlay{position:absolute; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.65); z-index:1;} .kategori-metin{position:relative; z-index:2; color:white; font-size:26px; font-weight:bold; letter-spacing:1px;}</style></head><body><div class='header-bar'><a href='/' style='text-decoration:none; color:white;'>Geri</a><h2 style='margin:0;'>YENİDEN</h2><div style='width:60px;'></div></div><div class='container'><div class='bölüm-başlığı'>Kategoriler</div>"
    for kat in kategoriler:
        resim = RESIM_MAP.get(kat[0], VARSAYILAN_RESIM)
        html += f"<a href='/kategori/{kat[0]}' class='kategori-kartı' style='background-image: url(\"{resim}\");'><div class='overlay'></div><div class='kategori-metin'>{kat[0]}</div></a>"
    html += "</div></body></html>"
    cursor.close(); baglanti.close()
    return html

# --- KATEGORİ DETAY ---
@app.route('/kategori/<ad>')
def kategori_detay(ad):
    baglanti = veritabanina_baglan()
    cursor = baglanti.cursor()
    cursor.execute("SELECT Urunler.urun_adi, Urunler.fiyat FROM Urunler INNER JOIN Kategoriler ON Urunler.kategori_id = Kategoriler.kategori_id WHERE Kategoriler.kategori_adi = %s ORDER BY Urunler.urun_adi", (ad,))
    urunler = cursor.fetchall()
    resim = RESIM_MAP.get(ad, VARSAYILAN_RESIM)
    html = f"<html><head><meta name='viewport' content='width=device-width, initial-scale=1.0'><style>body{{font-family:'Segoe UI', sans-serif; background-color:#121212; color:#ffffff; max-width:600px; margin:auto;}} .hero-header{{position:relative; height:260px; background-image:url('{resim}'); background-size:cover; background-position:center;}} .urun-karti{{margin:15px; display:flex; justify-content:space-between; background:#1a1a1a; padding:20px; border-radius:8px; border-left:4px solid #e65100;}}</style></head><body><div class='hero-header'><h1 style='position:absolute; bottom:10px; left:20px; color:white;'>{ad}</h1></div>"
    for u in urunler:
        html += f"<div class='urun-karti'><span>{u[0]}</span><span style='font-weight:bold; color:#e65100;'>{u[1]} TL</span></div>"
    html += "<a href='/menu' style='display:block; text-align:center; padding:20px; color:#e65100; text-decoration:none;'>Geri Dön</a></body></html>"
    cursor.close(); baglanti.close()
    return html

from flask import Flask
import os
from admin import admin_bp  # admin.py'yi çağır

app = Flask(__name__)
app.secret_key = 'pinar23_gizli_anahtar'

# Admin paneli artık restoran.py'nin bir parçası
app.register_blueprint(admin_bp)

# ... (Kendi veritabanı fonksiyonların ve menü kodların aynen kalsın) ...

# ... (Kendi veritabanı fonksiyonların ve diğer tüm kodların olduğu gibi kalacak) ...
# --- VERİTABANI BAĞLANTI FONKSİYONU ---
def veritabanina_baglan():
    # Sadece ortam değişkenini kullan, asla şifreyi buraya yazma
    DATABASE_URL = os.environ.get('DATABASE_URL')
    
    # sslmode='require' Render'da veritabanı bağlantısı için gereklidir
    return psycopg2.connect(DATABASE_URL, sslmode='require')

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

# --- YENİ EKLENEN ANA SAYFA (GİRİŞ EKRANI) ---
@app.route('/')
def ana_sayfa():
    return """
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body { font-family: 'Segoe UI', Tahoma, sans-serif; background: url('https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=1200&auto=format&fit=crop') center/cover no-repeat; margin: 0; height: 100vh; }
            .overlay { background: rgba(15, 15, 15, 0.85); height: 100%; display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center; padding: 20px; }
            .brand-logo { font-size: 48px; color: #ffffff; font-weight: 900; letter-spacing: 2px; margin-bottom: 15px; text-transform: uppercase; border-bottom: 3px solid #e65100; padding-bottom: 10px; }
            .subtitle { font-size: 18px; color: #dcdde1; margin-bottom: 40px; font-weight: 300; max-width: 400px; line-height: 1.6; }
            .btn-menu { text-decoration: none; background-color: #e65100; color: white; padding: 18px 45px; border-radius: 8px; font-size: 18px; font-weight: bold; transition: 0.3s; letter-spacing: 1px; text-transform: uppercase; }
            .btn-menu:hover { background-color: #ff6600; }
        </style>
    </head>
    <body>
        <div class="overlay">
            <div class="brand-logo">YENİDEN</div>
            <div class="subtitle">Özenle seçilmiş malzemeler, usta ellerden çıkan eşsiz tarifler. Gerçek lezzet deneyimine davetlisiniz.</div>
            <a href="/menu" class="btn-menu">Menüyü Keşfet</a>
        </div>
    </body>
    </html>
    """

# ==========================================
# 3. ROTA: KATEGORİLER LİSTESİ (/menu)
# ==========================================
@app.route('/menu')
def menu_getir():
    baglanti = veritabanina_baglan()
    cursor = baglanti.cursor()
    cursor.execute("""
        SELECT DISTINCT Kategoriler.kategori_adi 
        FROM Urunler 
        INNER JOIN Kategoriler ON Urunler.kategori_id = Kategoriler.kategori_id
        ORDER BY Kategoriler.kategori_adi
    """)
    kategoriler = cursor.fetchall()
    
    html_ciktisi = """
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body { font-family: 'Segoe UI', Tahoma, sans-serif; background-color: #121212; color: #ffffff; max-width: 600px; margin: auto; padding: 0; padding-bottom: 50px; }
            .header-bar { display: flex; align-items: center; justify-content: space-between; padding: 18px 20px; background-color: #1a1a1a; position: sticky; top: 0; z-index: 1000; border-bottom: 1px solid #333; }
            .btn-geri { text-decoration: none; color: #ffffff; font-weight: 500; background: #2a2a2a; padding: 8px 16px; border-radius: 6px; font-size: 14px; border: 1px solid #444; }
            .brand-title { margin: 0; font-size: 22px; color: #ffffff; font-weight: 800; letter-spacing: 1px; }
            .container { padding: 25px 15px; }
            .bölüm-başlığı { font-size: 24px; color: #ffffff; margin: 0 5px 25px 5px; font-weight: 900; border-left: 4px solid #e65100; padding-left: 10px; }
            .kategori-listesi { display: flex; flex-direction: column; gap: 20px; }
            .kategori-kartı { position: relative; height: 150px; border-radius: 10px; overflow: hidden; background-size: cover; background-position: center; display: flex; align-items: center; justify-content: center; text-decoration: none; box-shadow: 0 8px 20px rgba(0,0,0,0.5); border: 1px solid #333; }
            .overlay { position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.65); z-index: 1; transition: background 0.3s; }
            .kategori-kartı:hover .overlay { background: rgba(0,0,0,0.45); }
            .kategori-metin { position: relative; z-index: 2; color: white; font-size: 26px; font-weight: bold; letter-spacing: 1px; text-shadow: 0 4px 10px rgba(0,0,0,0.9); }
        </style>
    </head>
    <body>
        <div class="header-bar">
            <a href="/" class="btn-geri">Geri</a>
            <h2 class="brand-title">YENİDEN</h2>
            <div style='width:60px;'></div>
        </div>
        <div class="container">
            <div class="bölüm-başlığı">Kategoriler</div>
            <div class="kategori-listesi">
    """
    for kat in kategoriler:
        resim_url = RESIM_MAP.get(kat[0], VARSAYILAN_RESIM)
        html_ciktisi += f"<a href='/kategori/{kat[0]}' class='kategori-kartı' style='background-image: url(\"{resim_url}\");'><div class='overlay'></div><div class='kategori-metin'>{kat[0]}</div></a>"
    html_ciktisi += "</div></div></body></html>"
    cursor.close()
    baglanti.close()
    return html_ciktisi

# ==========================================
# 4. ROTA: KATEGORİ DETAY (/kategori/<ad>)
# ==========================================
@app.route('/kategori/<ad>')
def kategori_detay(ad):
    baglanti = veritabanina_baglan()
    cursor = baglanti.cursor()
    cursor.execute("""
        SELECT Urunler.urun_adi, Urunler.fiyat 
        FROM Urunler 
        INNER JOIN Kategoriler ON Urunler.kategori_id = Kategoriler.kategori_id
        WHERE Kategoriler.kategori_adi = %s
        ORDER BY Urunler.urun_adi
    """, (ad,))
    urunler = cursor.fetchall()
    resim_url = RESIM_MAP.get(ad, VARSAYILAN_RESIM)
    
    html_ciktisi = f"""
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, sans-serif; background-color: #121212; color: #ffffff; max-width: 600px; margin: auto; padding: 0; padding-bottom: 50px; }}
            .hero-header {{ position: relative; height: 260px; background-image: url('{resim_url}'); background-size: cover; background-position: center; box-shadow: 0 10px 30px rgba(0,0,0,0.8); margin-bottom: 30px; border-bottom: 1px solid #333; }}
            .hero-overlay {{ position: absolute; top:0; left:0; width:100%; height:100%; background: linear-gradient(to bottom, rgba(0,0,0,0.2) 0%, rgba(18,18,18,1) 100%); }}
            .btn-geri-float {{ position: absolute; top: 20px; left: 20px; z-index: 10; text-decoration: none; color: #ffffff; background: rgba(26,26,26,0.8); padding: 10px 18px; border-radius: 6px; font-weight: bold; font-size: 14px; border: 1px solid #444; backdrop-filter: blur(4px); }}
            .hero-title {{ position: absolute; bottom: 15px; left: 25px; z-index: 10; color: white; font-size: 34px; font-weight: 900; margin: 0; letter-spacing: 1px; }}
            .urun-listesi {{ padding: 0 15px; }}
            .urun-karti {{ margin: 0 5px 15px 5px; display: flex; justify-content: space-between; align-items: center; background: #1a1a1a; padding: 22px 20px; border-radius: 8px; border: 1px solid #2a2a2a; box-shadow: 0 4px 15px rgba(0,0,0,0.3); border-left: 4px solid transparent; transition: 0.2s; }}
            .urun-karti:hover {{ border-left: 4px solid #e65100; background: #222222; }}
            .urun-adi {{ font-size: 17px; font-weight: 500; color: #e0e0e0; letter-spacing: 0.5px; }}
            .urun-fiyat {{ font-size: 19px; font-weight: 800; color: #e65100; }}
        </style>
    </head>
    <body>
        <div class="hero-header">
            <div class="hero-overlay"></div>
            <a href="/menu" class="btn-geri-float">Geri</a>
            <h1 class="hero-title">{ad}</h1>
        </div>
        <div class="urun-listesi">
    """
    for urun in urunler:
        html_ciktisi += f"""
            <div class="urun-karti">
                <span class="urun-adi">{urun[0]}</span>
                <span class="urun-fiyat">{urun[1]} ₺</span>
            </div>
        """
    html_ciktisi += "</div></body></html>"
    cursor.close()
    baglanti.close()
    return html_ciktisi


if __name__ == '__main__':
    

éfrom flask import Flask, request
import psycopg2
import os # Şifreleri gizlemek için gerekli kütüphane

app = Flask(__name__)

# --- VERİTABANI BAĞLANTISI (GÜVENLİ) ---
def veritabanina_baglan():
    # Eğer Render'daysak DATABASE_URL'i kullan, yereldeysek eski sisteme devam et
    if 'DATABASE_URL' in os.environ:
        return psycopg2.connect(os.environ['DATABASE_URL'])
    else:
        # Kendi bilgisayarındaki yerel ayarların
        return psycopg2.connect(
            dbname=os.environ.get('DB_NAME', 'restoran_db'),
            user=os.environ.get('DB_USER', 'postgres'),
            password=os.environ.get('DB_PASSWORD', 'pinar23.'),
            host=os.environ.get('DB_HOST', 'localhost'),
            port=os.environ.get('DB_PORT', '5432')
        )
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

# --- ROTALAR ---
@app.route('/')
def ana_sayfa():
    return """
    <html><head><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { font-family: 'Segoe UI', sans-serif; background: url('https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=1200&auto=format&fit=crop') center/cover; margin: 0; height: 100vh; }
        .overlay { background: rgba(15, 15, 15, 0.85); height: 100%; display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center; padding: 20px; }
        .brand-logo { font-size: 48px; color: #ffffff; font-weight: 900; margin-bottom: 15px; border-bottom: 3px solid #e65100; }
        .btn-menu { text-decoration: none; background-color: #e65100; color: white; padding: 18px 45px; border-radius: 8px; font-weight: bold; }
    </style></head>
    <body><div class="overlay"><div class="brand-logo">YENİDEN</div><a href="/menu" class="btn-menu">MENÜYÜ KEŞFET</a></div></body></html>
    """

@app.route('/menu')
def menu_getir():
    baglanti = veritabanina_baglan()
    cursor = baglanti.cursor()
    cursor.execute("SELECT DISTINCT k.kategori_adi FROM Urunler u INNER JOIN Kategoriler k ON u.kategori_id = k.kategori_id ORDER BY k.kategori_adi")
    kategoriler = cursor.fetchall()
    
    html = '<html><head><meta name="viewport" content="width=device-width, initial-scale=1.0"><style>body{background:#121212; color:#fff; max-width:600px; margin:auto; font-family:sans-serif;}</style></head><body>'
    html += '<div style="padding:20px;"><h2>Kategoriler</h2>'
    for kat in kategoriler:
        resim = RESIM_MAP.get(kat[0], VARSAYILAN_RESIM)
        html += f"<a href='/kategori/{kat[0]}' style='display:block; height:150px; margin-bottom:20px; background:url(\"{resim}\") center/cover; border-radius:10px; display:flex; align-items:center; justify-content:center; text-decoration:none; color:white; font-size:24px; font-weight:bold; border:1px solid #333;'>{kat[0]}</a>"
    html += "</div></body></html>"
    cursor.close(); baglanti.close()
    return html

@app.route('/kategori/<ad>')
def kategori_detay(ad):
    baglanti = veritabanina_baglan()
    cursor = baglanti.cursor()
    cursor.execute("SELECT u.urun_adi, u.fiyat FROM Urunler u JOIN Kategoriler k ON u.kategori_id = k.kategori_id WHERE k.kategori_adi = %s", (ad,))
    urunler = cursor.fetchall()
    html = f"<html><body><div style='background:#121212; color:white; padding:20px;'><h1>{ad}</h1>"
    for u in urunler:
        html += f"<div style='background:#1a1a1a; padding:15px; margin-bottom:10px; border-radius:8px; display:flex; justify-content:space-between;'><span>{u[0]}</span><span>{u[1]} ₺</span></div>"
    html += "<a href='/menu' style='display:block; padding:10px; background:#e65100; color:white; text-align:center; text-decoration:none; margin-top:20px;'>Geri</a></div></body></html>"
    cursor.close(); baglanti.close()
    return html

if __name__ == '__main__':
    # Bulut sunucular için port ayarı
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
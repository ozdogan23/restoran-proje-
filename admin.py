from flask import Blueprint, request, redirect, url_for, session

# 'admin' ismi, bu dosyadaki rotaların /admin ile başlayacağını Flask'a söyler
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/giris', methods=['GET', 'POST']) # Bu artık /admin/giris olur
def admin_giris():
    # ... (giriş kodların aynı kalsın) ...

@admin_bp.route('/') # Bu artık /admin/ olur
def admin_anasayfa():
    # ... (diğer kodların aynı kalsın) ...

from flask import Flask, request, redirect, url_for, session
import psycopg2
import os # Şifreleri gizlemek için eklendi

admin_app = Flask(__name__)
# Gizli anahtarını da artık ortam değişkeninden (OS) alacağız
admin_app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'pinar23_gizli_anahtar')
# Şifreni ortam değişkenlerinden al, yoksa varsayılanı kullan
ADMIN_SIFRE = os.environ.get('ADMIN_SIFRE', '1234')

def veritabanina_baglan():
    # Veritabanı bilgilerini de ortam değişkenlerinden alırsak sunucuda çok daha güvenli olur
    return psycopg2.connect(
        dbname=os.environ.get('DB_NAME', 'restoran_db'),
        user=os.environ.get('DB_USER', 'postgres'),
        password=os.environ.get('DB_PASSWORD', 'pinar23.'),
        host=os.environ.get('DB_HOST', 'localhost'),
        port=os.environ.get('DB_PORT', '5432')
    )

def sayfa_yapisi(icerik):
    return f"""
    <!DOCTYPE html>
    <html><head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{ font-family: 'Segoe UI', sans-serif; background: #121212; color: #fff; margin:0; min-height:100vh; display: flex; justify-content: center; align-items: center; padding: 20px; }}
        .container {{ width: 90%; max-width: 500px; background: #1a1a1a; padding: 30px; border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.8); border: 1px solid #333; box-sizing: border-box; }}
        h2, h3 {{ color: #e65100; text-align: center; margin-bottom: 20px; }}
        input, select {{ width: 100%; padding: 15px; margin: 10px 0; background: #222; border: 1px solid #444; border-radius: 8px; color: white; box-sizing: border-box; font-size: 16px; }}
        button {{ width: 100%; padding: 15px; margin-top: 10px; background: #e65100; border: none; color: white; font-weight: bold; border-radius: 8px; cursor: pointer; font-size: 16px; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 20px; color: white; font-size: 14px; }}
        th {{ background: #222; padding: 10px; border-bottom: 2px solid #333; }}
        td {{ padding: 10px; border-bottom: 1px solid #333; text-align: center; }}
        a {{ color: #00bcd4; text-decoration: none; font-weight: bold; margin: 0 5px; }}
        .btn {{ display: block; width: 100%; text-align: center; background: #e65100; color: white; padding: 12px; border-radius: 8px; text-decoration: none; margin-top: 15px; box-sizing: border-box; }}
    </style></head><body>
    <div class="container">{icerik}</div>
    </body></html>"""

@admin_app.before_request
def guvenlik():
    if request.endpoint and 'admin' in request.endpoint and 'admin_giris' not in request.endpoint:
        if not session.get('giris'): return redirect(url_for('admin_giris'))

@admin_app.route('/admin/giris', methods=['GET', 'POST'])
def admin_giris():
    if request.method == 'POST':
        if request.form['sifre'] == ADMIN_SIFRE:
            session['giris'] = True
            return redirect(url_for('admin_anasayfa'))
        return sayfa_yapisi("<h3>Hatalı Şifre!</h3><a href='/admin/giris' class='btn'>Tekrar Dene</a>")
    return sayfa_yapisi("<form method='POST'><h2>Admin Girişi</h2><input type='password' name='sifre' placeholder='Şifre' required><button type='submit'>Giriş Yap</button></form>")

@admin_app.route('/admin')
def admin_anasayfa():
    arama = request.args.get('q', '')
    baglanti = veritabanina_baglan()
    cursor = baglanti.cursor()
    query = "SELECT Urunler.urun_id, Urunler.urun_adi, Urunler.fiyat, Kategoriler.kategori_adi FROM Urunler JOIN Kategoriler ON Urunler.kategori_id = Kategoriler.kategori_id"
    if arama: query += f" WHERE Urunler.urun_adi ILIKE '%{arama}%'"
    cursor.execute(query + " ORDER BY Urunler.urun_id")
    urunler = cursor.fetchall()
    cursor.close(); baglanti.close()
    tablo = "".join([f"<tr><td>{u[1]}</td><td>{u[2]} TL</td><td>{u[3]}</td><td><a href='/admin/duzenle/{u[0]}'>✏️</a> | <a href='/admin/sil/{u[0]}' style='color:#ff4d4d;'>❌</a></td></tr>" for u in urunler])
    return sayfa_yapisi(f"<h2>🛠️ Yönetim Paneli</h2><form method='GET' action='/admin'><input name='q' placeholder='Ürün ara...' value='{arama}'></form><a href='/admin/ekle' class='btn'>+ Yeni Ürün Ekle</a><table><tr><th>Ürün</th><th>Fiyat</th><th>Kat.</th><th>İşlem</th></tr>{tablo}</table><a href='/admin/cikis' class='btn' style='background:#555;'>Oturumu Kapat</a>")

@admin_app.route('/admin/ekle', methods=['GET', 'POST'])
def urun_ekle():
    if request.method == 'POST':
        baglanti = veritabanina_baglan()
        cursor = baglanti.cursor()
        cursor.execute("INSERT INTO Urunler (urun_adi, fiyat, kategori_id) VALUES (%s, %s, %s)", (request.form['ad'], request.form['fiyat'], request.form['kategori_id']))
        baglanti.commit(); cursor.close(); baglanti.close()
        return redirect(url_for('admin_anasayfa'))
    baglanti = veritabanina_baglan()
    cursor = baglanti.cursor()
    cursor.execute("SELECT kategori_id, kategori_adi FROM Kategoriler")
    kategoriler = cursor.fetchall()
    cursor.close(); baglanti.close()
    opts = "".join([f'<option value="{k[0]}">{k[1]}</option>' for k in kategoriler])
    return sayfa_yapisi(f"<form method='POST'><h3>Yeni Ürün Ekle</h3><input name='ad' placeholder='Ürün Adı' required><input name='fiyat' placeholder='Fiyat' required><select name='kategori_id'>{opts}</select><button type='submit'>Kaydet</button></form>")

@admin_app.route('/admin/duzenle/<int:id>', methods=['GET', 'POST'])
def urun_duzenle(id):
    baglanti = veritabanina_baglan()
    cursor = baglanti.cursor()
    if request.method == 'POST':
        cursor.execute("UPDATE Urunler SET urun_adi=%s, fiyat=%s WHERE urun_id=%s", (request.form['ad'], request.form['fiyat'], id))
        baglanti.commit(); cursor.close(); baglanti.close()
        return redirect(url_for('admin_anasayfa'))
    cursor.execute("SELECT urun_adi, fiyat FROM Urunler WHERE urun_id=%s", (id,))
    u = cursor.fetchone()
    cursor.close(); baglanti.close()
    return sayfa_yapisi(f"<form method='POST'><h3>Düzenle</h3><input name='ad' value='{u[0]}' required><input name='fiyat' value='{u[1]}' required><button type='submit'>Güncelle</button></form>")

@admin_app.route('/admin/sil/<int:id>')
def urun_sil(id):
    baglanti = veritabanina_baglan()
    cursor = baglanti.cursor()
    cursor.execute("DELETE FROM Urunler WHERE urun_id = %s", (id,))
    baglanti.commit(); cursor.close(); baglanti.close()
    return redirect(url_for('admin_anasayfa'))

@admin_app.route('/admin/cikis')
def admin_cikis():
    session.pop('giris', None)
    return redirect(url_for('admin_giris'))

if __name__ == '__main__':
    admin_app.run(port=5000, debug=True)

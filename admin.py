from flask import Blueprint, request, redirect, url_for, session
import psycopg2
import os

# Blueprint tanımlaması (url_prefix ile otomatik /admin ekler)
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')
ADMIN_SIFRE = "1234"

def veritabanina_baglan():
    return psycopg2.connect(os.environ.get('DATABASE_URL'), sslmode='require')

def sayfa_yapisi(icerik):
    return f"""
    <!DOCTYPE html><html><head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{ font-family: 'Segoe UI', sans-serif; background: #121212; color: #fff; margin:0; min-height:100vh; display: flex; justify-content: center; align-items: center; padding: 20px; }}
        .container {{ width: 90%; max-width: 500px; background: #1a1a1a; padding: 30px; border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.8); border: 1px solid #333; }}
        input, select {{ width: 100%; padding: 15px; margin: 10px 0; background: #222; border: 1px solid #444; border-radius: 8px; color: white; box-sizing: border-box; }}
        button {{ width: 100%; padding: 15px; margin-top: 10px; background: #e65100; border: none; color: white; font-weight: bold; border-radius: 8px; cursor: pointer; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 20px; color: white; }}
        th {{ background: #222; padding: 10px; border-bottom: 2px solid #333; }}
        td {{ padding: 10px; border-bottom: 1px solid #333; text-align: center; }}
        .btn {{ display: block; width: 100%; text-align: center; background: #e65100; color: white; padding: 12px; border-radius: 8px; text-decoration: none; margin-top: 15px; }}
    </style></head><body><div class="container">{icerik}</div></body></html>"""

# Artık admin_bp kullanıyoruz
@admin_bp.before_request
def guvenlik():
    if 'giris' not in session and request.endpoint != 'admin.admin_giris':
        return redirect(url_for('admin.admin_giris'))

@admin_bp.route('/giris', methods=['GET', 'POST'])
def admin_giris():
    if request.method == 'POST':
        if request.form['sifre'] == ADMIN_SIFRE:
            session['giris'] = True
            return redirect(url_for('admin.admin_anasayfa'))
        return sayfa_yapisi("<h3>Hatalı Şifre!</h3><a href='/admin/giris' class='btn'>Tekrar Dene</a>")
    return sayfa_yapisi("<form method='POST'><h2>Admin Girişi</h2><input type='password' name='sifre' placeholder='Şifre' required><button type='submit'>Giriş Yap</button></form>")

@admin_bp.route('/')
def admin_anasayfa():
    baglanti = veritabanina_baglan()
    cursor = baglanti.cursor()
    cursor.execute("SELECT Urunler.urun_id, Urunler.urun_adi, Urunler.fiyat, Kategoriler.kategori_adi FROM Urunler JOIN Kategoriler ON Urunler.kategori_id = Kategoriler.kategori_id ORDER BY Urunler.urun_id")
    urunler = cursor.fetchall()
    cursor.close(); baglanti.close()
    tablo = "".join([f"<tr><td>{u[1]}</td><td>{u[2]} TL</td><td>{u[3]}</td><td><a href='/admin/duzenle/{u[0]}'>✏️</a> | <a href='/admin/sil/{u[0]}' style='color:#ff4d4d;'>❌</a></td></tr>" for u in urunler])
    return sayfa_yapisi(f"<h2>🛠️ Yönetim Paneli</h2><a href='/admin/ekle' class='btn'>+ Yeni Ürün Ekle</a><table><tr><th>Ürün</th><th>Fiyat</th><th>Kat.</th><th>İşlem</th></tr>{tablo}</table><a href='/admin/cikis' class='btn' style='background:#555;'>Oturumu Kapat</a>")

@admin_bp.route('/ekle', methods=['GET', 'POST'])
def urun_ekle():
    if request.method == 'POST':
        baglanti = veritabanina_baglan()
        cursor = baglanti.cursor()
        cursor.execute("INSERT INTO Urunler (urun_adi, fiyat, kategori_id) VALUES (%s, %s, %s)", (request.form['ad'], request.form['fiyat'], request.form['kategori_id']))
        baglanti.commit(); cursor.close(); baglanti.close()
        return redirect(url_for('admin.admin_anasayfa'))
    return sayfa_yapisi("<form method='POST'><h3>Yeni Ürün Ekle</h3><input name='ad' placeholder='Ürün Adı' required><input name='fiyat' placeholder='Fiyat' required><input name='kategori_id' placeholder='Kategori ID' required><button type='submit'>Kaydet</button></form>")

@admin_bp.route('/duzenle/<int:id>', methods=['GET', 'POST'])
def urun_duzenle(id):
    baglanti = veritabanina_baglan()
    cursor = baglanti.cursor()
    if request.method == 'POST':
        cursor.execute("UPDATE Urunler SET urun_adi=%s, fiyat=%s WHERE urun_id=%s", (request.form['ad'], request.form['fiyat'], id))
        baglanti.commit(); cursor.close(); baglanti.close()
        return redirect(url_for('admin.admin_anasayfa'))
    cursor.execute("SELECT urun_adi, fiyat FROM Urunler WHERE urun_id=%s", (id,))
    u = cursor.fetchone()
    cursor.close(); baglanti.close()
    return sayfa_yapisi(f"<form method='POST'><h3>Düzenle</h3><input name='ad' value='{u[0]}' required><input name='fiyat' value='{u[1]}' required><button type='submit'>Güncelle</button></form>")

@admin_bp.route('/sil/<int:id>')
def urun_sil(id):
    baglanti = veritabanina_baglan()
    cursor = baglanti.cursor()
    cursor.execute("DELETE FROM Urunler WHERE urun_id = %s", (id,))
    baglanti.commit(); cursor.close(); baglanti.close()
    return redirect(url_for('admin.admin_anasayfa'))

@admin_bp.route('/cikis')
def admin_cikis():
    session.pop('giris', None)
    return redirect(url_for('admin.admin_giris'))

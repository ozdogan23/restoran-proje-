from flask import Blueprint, request, redirect, url_for, session
import psycopg2
import os

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Buraya kendi bağlantı fonksiyonunu tekrar ekle (bağımsız olsun)
def veritabanina_baglan():
    return psycopg2.connect(os.environ.get('DATABASE_URL'), sslmode='require')

# ... (admin.py kodlarının geri kalanı aynı kalsın) ...
def sayfa_yapisi(icerik):
    return f"""
    <!DOCTYPE html><html><head><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{ font-family: 'Segoe UI', sans-serif; background: #121212; color: #fff; margin:0; padding: 20px; display: flex; justify-content: center; }}
        .container {{ width: 90%; max-width: 500px; background: #1a1a1a; padding: 20px; border-radius: 10px; }}
        input, select {{ width: 100%; padding: 10px; margin: 5px 0; background: #222; border: 1px solid #444; color: white; border-radius: 5px; }}
        button {{ width: 100%; padding: 10px; background: #e65100; border: none; color: white; font-weight: bold; cursor: pointer; border-radius: 5px; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 15px; color: white; }}
        td, th {{ padding: 10px; border-bottom: 1px solid #333; text-align: center; }}
        a {{ color: #00bcd4; text-decoration: none; }}
        .btn {{ display: block; text-align: center; background: #e65100; color: white; padding: 10px; border-radius: 5px; margin-top: 10px; }}
    </style></head><body><div class="container">{icerik}</div></body></html>"""

@admin_bp.before_request
def guvenlik():
    if 'giris' not in session and request.endpoint != 'admin.admin_giris':
        return redirect(url_for('admin.admin_giris'))

@admin_bp.route('/giris', methods=['GET', 'POST'])
def admin_giris():
    if request.method == 'POST':
        if request.form['sifre'] == "1234":
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
    return sayfa_yapisi(f"<h2>🛠️ Yönetim</h2><a href='/admin/ekle' class='btn'>+ Yeni Ürün</a><table><tr><th>Ürün</th><th>Fiyat</th><th>Kat.</th><th>İşlem</th></tr>{tablo}</table><a href='/admin/cikis' class='btn' style='background:#555;'>Çıkış</a>")

@admin_bp.route('/ekle', methods=['GET', 'POST'])
def urun_ekle():
    if request.method == 'POST':
        baglanti = veritabanina_baglan()
        cursor = baglanti.cursor()
        cursor.execute("INSERT INTO Urunler (urun_adi, fiyat, kategori_id) VALUES (%s, %s, %s)", (request.form['ad'], request.form['fiyat'], request.form['kategori_id']))
        baglanti.commit(); cursor.close(); baglanti.close()
        return redirect(url_for('admin.admin_anasayfa'))
    return sayfa_yapisi("<form method='POST'><h3>Ekle</h3><input name='ad' placeholder='Ad' required><input name='fiyat' placeholder='Fiyat' required><input name='kategori_id' placeholder='Kategori ID' required><button type='submit'>Kaydet</button></form>")

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

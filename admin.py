from flask import Blueprint, request, redirect, url_for, session
import psycopg2
import os

# admin_bp ismini Blueprint olarak tanımlıyoruz
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

ADMIN_SIFRE = os.environ.get('ADMIN_SIFRE', '1234')

def veritabanina_baglan():
    return psycopg2.connect(os.environ.get('DATABASE_URL'), sslmode='require')

def sayfa_yapisi(icerik):
    return f"""
    <!DOCTYPE html><html><head><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{ font-family: sans-serif; background: #121212; color: #fff; display: flex; justify-content: center; padding: 20px; }}
        .container {{ width: 90%; max-width: 500px; background: #1a1a1a; padding: 30px; border-radius: 20px; }}
        input {{ width: 100%; padding: 10px; margin: 5px 0; background: #222; border: 1px solid #444; color: white; }}
        button {{ width: 100%; padding: 10px; background: #e65100; border: none; color: white; cursor: pointer; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
        td, th {{ padding: 10px; border-bottom: 1px solid #333; }}
        .btn {{ display: block; text-align: center; background: #e65100; padding: 10px; text-decoration: none; color: white; margin-top: 10px; }}
    </style></head><body><div class="container">{icerik}</div></body></html>"""

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
    return sayfa_yapisi("<form method='POST'><h2>Admin Girişi</h2><input type='password' name='sifre' required><button type='submit'>Giriş Yap</button></form>")

@admin_bp.route('/')
def admin_anasayfa():
    baglanti = veritabanina_baglan()
    cursor = baglanti.cursor()
    cursor.execute("SELECT urun_id, urun_adi, fiyat FROM Urunler")
    urunler = cursor.fetchall()
    cursor.close(); baglanti.close()
    tablo = "".join([f"<tr><td>{u[1]}</td><td>{u[2]} TL</td><td><a href='/admin/sil/{u[0]}'>❌</a></td></tr>" for u in urunler])
    return sayfa_yapisi(f"<h2>Yönetim</h2><table>{tablo}</table><a href='/admin/cikis' class='btn'>Çıkış</a>")

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

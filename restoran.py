import os
from flask import Flask, request, redirect, url_for, session
import psycopg2

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'pinar23_gizli_anahtar')
ADMIN_SIFRE = os.environ.get('ADMIN_SIFRE', '1234')

def veritabanina_baglan():
    if 'DATABASE_URL' in os.environ:
        return psycopg2.connect(os.environ['DATABASE_URL'])
    else:
        return psycopg2.connect(
            dbname=os.environ.get('DB_NAME', 'restoran_db'),
            user=os.environ.get('DB_USER', 'postgres'),
            password=os.environ.get('DB_PASSWORD', 'pinar23.'),
            host=os.environ.get('DB_HOST', 'localhost'),
            port=os.environ.get('DB_PORT', '5432')
        )

RESIM_MAP = {
    "Ana Yemekler": "https://images.unsplash.com/photo-1544025162-d76694265947?w=600&auto=format&fit=crop",
    "Dondurmalar": "https://images.unsplash.com/photo-1563805042-7684c019e1cb?w=600&auto=format&fit=crop",
    "Kahveler": "https://images.unsplash.com/photo-1509042239860-f550ce710b93?w=600&auto=format&fit=crop",
    "Soğuk İçecekler": "https://images.unsplash.com/photo-1513558161293-cdaf765ed2fd?w=600&auto=format&fit=crop",
    "Sıcak İçecekler": "https://images.unsplash.com/photo-1544787219-7f47ccb76574?w=600&auto=format&fit=crop",
    "Tatlılar": "https://images.unsplash.com/photo-1551024601-bec78aea704b?w=600&auto=format&fit=crop"
}
VARSAYILAN_RESIM = "https://images.unsplash.com/photo-1498654896293-37aacf113fd9?w=600&auto=format&fit=crop"

@app.route('/')
def ana_sayfa():
    return "<html><body style='background:#121212; color:#fff; text-align:center; padding-top:100px;'><h1>YENİDEN</h1><a href='/menu' style='color:#e65100; font-size:24px;'>Menüyü Keşfet</a></body></html>"

@app.route('/menu')
def menu_getir():
    baglanti = veritabanina_baglan()
    cursor = baglanti.cursor()
    cursor.execute("SELECT DISTINCT Kategoriler.kategori_adi FROM Urunler INNER JOIN Kategoriler ON Urunler.kategori_id = Kategoriler.kategori_id ORDER BY Kategoriler.kategori_adi")
    kategoriler = cursor.fetchall()
    html = "<html><body style='background:#121212; color:#fff; text-align:center;'>"
    for kat in kategoriler:
        html += f"<a href='/kategori/{kat[0]}' style='display:block; padding:20px; color:#fff; text-decoration:none;'>{kat[0]}</a>"
    html += "</body></html>"
    cursor.close(); baglanti.close()
    return html

@app.route('/kategori/<ad>')
def kategori_detay(ad):
    baglanti = veritabanina_baglan()
    cursor = baglanti.cursor()
    cursor.execute("SELECT urun_adi, fiyat FROM Urunler INNER JOIN Kategoriler ON Urunler.kategori_id = Kategoriler.kategori_id WHERE Kategoriler.kategori_adi = %s", (ad,))
    urunler = cursor.fetchall()
    html = f"<html><body style='background:#121212; color:#fff;'><h1>{ad}</h1>"
    for u in urunler:
        html += f"<p>{u[0]} - {u[1]} TL</p>"
    html += "<a href='/menu'>Geri</a></body></html>"
    cursor.close(); baglanti.close()
    return html

# --- ADMIN PANEL ---
def sayfa_yapisi(icerik):
    return f"<html><body style='background:#1a1a1a; color:#fff; padding:20px;'>{icerik}</body></html>"

@app.before_request
def guvenlik():
    if request.path.startswith('/admin') and request.path != '/admin/giris':
        if not session.get('giris'): return redirect(url_for('admin_giris'))

@app.route('/admin/giris', methods=['GET', 'POST'])
def admin_giris():
    if request.method == 'POST':
        if request.form['sifre'] == ADMIN_SIFRE:
            session['giris'] = True
            return redirect(url_for('admin_anasayfa'))
        return "Hatalı şifre"
    return sayfa_yapisi("<form method='POST'><input name='sifre' type='password'><button>Giriş</button></form>")

@app.route('/admin')
def admin_anasayfa():
    baglanti = veritabanina_baglan()
    cursor = baglanti.cursor()
    cursor.execute("SELECT urun_id, urun_adi, fiyat FROM Urunler")
    urunler = cursor.fetchall()
    tablo = "".join([f"<tr><td>{u[1]}</td><td>{u[2]}</td><td><a href='/admin/sil/{u[0]}'>Sil</a></td></tr>" for u in urunler])
    return sayfa_yapisi(f"<h2>Admin Paneli</h2><a href='/admin/ekle'>+ Ekle</a><table>{tablo}</table>")

@app.route('/admin/ekle', methods=['GET', 'POST'])
def urun_ekle():
    if request.method == 'POST':
        baglanti = veritabanina_baglan()
        cursor = baglanti.cursor()
        cursor.execute("INSERT INTO Urunler (urun_adi, fiyat, kategori_id) VALUES (%s, %s, %s)", (request.form['ad'], request.form['fiyat'], 1))
        baglanti.commit(); cursor.close(); baglanti.close()
        return redirect(url_for('admin_anasayfa'))
    return sayfa_yapisi("<form method='POST'><input name='ad'><input name='fiyat'><button>Kaydet</button></form>")

@app.route('/admin/sil/<int:id>')
def urun_sil(id):
    baglanti = veritabanina_baglan()
    cursor = baglanti.cursor()
    cursor.execute("DELETE FROM Urunler WHERE urun_id = %s", (id,))
    baglanti.commit(); cursor.close(); baglanti.close()
    return redirect(url_for('admin_anasayfa'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)

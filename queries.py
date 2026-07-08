# queries.py

# Ürünleri ve kategorileri listeleyen ana sorgu
GET_URUNLER = """
    SELECT Urunler.urun_id, Urunler.urun_adi, Urunler.fiyat, Kategoriler.kategori_adi 
    FROM Urunler 
    JOIN Kategoriler ON Urunler.kategori_id = Kategoriler.kategori_id 
    ORDER BY Urunler.urun_id
"""

# Arama sorgusu (bunu fonksiyonla birleştireceğiz)
SEARCH_URUNLER = """
    SELECT Urunler.urun_id, Urunler.urun_adi, Urunler.fiyat, Kategoriler.kategori_adi 
    FROM Urunler 
    JOIN Kategoriler ON Urunler.kategori_id = Kategoriler.kategori_id 
    WHERE Urunler.urun_adi ILIKE %s
"""

# Ürün ekleme
INSERT_URUN = "INSERT INTO Urunler (urun_adi, fiyat, kategori_id) VALUES (%s, %s, %s)"

# Ürün güncelleme
UPDATE_URUN = "UPDATE Urunler SET urun_adi=%s, fiyat=%s WHERE urun_id=%s"

# Ürün silme
DELETE_URUN = "DELETE FROM Urunler WHERE urun_id = %s"

# Kategori listesi
GET_KATEGORILER = "SELECT kategori_id, kategori_adi FROM Kategoriler"

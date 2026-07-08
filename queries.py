# queries.py
GET_KATEGORILER = """
    SELECT DISTINCT Kategoriler.kategori_adi 
    FROM Urunler 
    INNER JOIN Kategoriler ON Urunler.kategori_id = Kategoriler.kategori_id 
    ORDER BY Kategoriler.kategori_adi
"""

GET_URUNLER_BY_KATEGORI = """
    SELECT Urunler.urun_adi, Urunler.fiyat 
    FROM Urunler 
    INNER JOIN Kategoriler ON Urunler.kategori_id = Kategoriler.kategori_id 
    WHERE Kategoriler.kategori_adi = %s 
    ORDER BY Urunler.urun_adi
"""

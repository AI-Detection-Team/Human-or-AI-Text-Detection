import google.generativeai as genai
import pandas as pd
import time
import random
import os
from dotenv import load_dotenv

# .env dosyasından API key'i yükle
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")

if not API_KEY:
    raise ValueError("GOOGLE_API_KEY bulunamadı! .env dosyasını kontrol edin.")

# ==========================================
# AYARLAR
# ==========================================
HEDEF_SAYI = 4000  # Toplam istenen veri
DOSYA_ADI = "ai_data.csv"
INSAN_VERISI_DOSYASI = "human_data.csv" # Konu başlığı kopya çekmek için

# API Ayarları
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash') # Hızlı ve ücretsiz model

def get_topics():
    """İnsan verisinden rastgele kelimeler alarak konu üretir"""
    try:
        df = pd.read_csv(INSAN_VERISI_DOSYASI)
        # Veri setinden rastgele 50 metin alıp ilk 5 kelimesini konu olarak kullan
        ornekler = df['text'].sample(n=50).tolist()
        konular = ["Computer Science", "Artificial Intelligence", "Machine Learning", "Cyber Security"]
        for metin in ornekler:
            konular.append(metin[:50]) # Metnin başını konu gibi al
        return konular
    except:
        return ["Computer Science", "Artificial Intelligence", "Software Engineering"]

def generate_ai_data():
    print(f"--- AI Veri Üretimi Başlıyor (Hedef: {HEDEF_SAYI}) ---")
    print("NOT: Ücretsiz sürüm kullanıldığı için her veri arası 4 saniye beklenecek.")

    # Mevcut veriyi kontrol et (Kaldığı yerden devam etsin)
    if os.path.exists(DOSYA_ADI):
        df_mevcut = pd.read_csv(DOSYA_ADI)
        ai_data = df_mevcut.to_dict('records')
        print(f"Mevcut dosya bulundu. {len(ai_data)} veriden devam ediliyor...")
    else:
        ai_data = []

    konu_listesi = get_topics()

    while len(ai_data) < HEDEF_SAYI:
        try:
            # Rastgele bir konu seç
            konu = random.choice(konu_listesi)

            # Gemini'ye giden emir (Prompt)
            prompt = f"Write a strictly academic abstract for a research paper about '{konu}'. It should be technically dense, about 6-8 sentences long. Do NOT add any introduction, title or conclusion. Just the abstract text."

            # İsteği gönder
            response = model.generate_content(prompt)

            # Gelen cevabı temizle
            text = response.text.replace("\n", " ").replace("*", "").strip()

            # Listeye ekle
            ai_data.append({"text": text, "label": "AI"})

            kalan = HEDEF_SAYI - len(ai_data)
            print(f"[{len(ai_data)}/{HEDEF_SAYI}] Üretildi. (Kalan: {kalan})")

            # Her 10 tanede bir kaydet (Güvenlik için)
            if len(ai_data) % 10 == 0:
                pd.DataFrame(ai_data).to_csv(DOSYA_ADI, index=False)
                print(f">> Dosya güncellendi ({len(ai_data)} veri).")

            # !!! ÖNEMLİ !!!
            # Google Free Tier limiti dakikada 15 istektir.
            # 4 saniye beklersek dakikada 15 istek sınırını aşmayız.
            time.sleep(4)

        except Exception as e:
            print(f"Hata oluştu (1 dakika bekleniyor...): {e}")
            time.sleep(60) # Hata alırsan (limit dolarsa) 1 dk dinlen

    # Döngü bitince son kez kaydet
    pd.DataFrame(ai_data).to_csv(DOSYA_ADI, index=False)
    print(f"\nTEBRİKLER! {HEDEF_SAYI} adet AI verisi başarıyla tamamlandı.")

if __name__ == "__main__":
    generate_ai_data()

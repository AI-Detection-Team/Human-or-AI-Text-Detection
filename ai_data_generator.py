import google.generativeai as genai
import pandas as pd
import time
import random
import os
from dotenv import load_dotenv

# 1. .env dosyasını yükle
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")

# ==========================================
# AYARLAR
# ==========================================
HEDEF_SAYI = 4000  # Toplam istenen veri
DOSYA_ADI = "ai_data.csv"
INSAN_VERISI_DOSYASI = "human_data.csv"

# API Ayarları
if not API_KEY:
    print("HATA: .env dosyasında GOOGLE_API_KEY bulunamadı!")
else:
    genai.configure(api_key=API_KEY)
    # Listeden bulduğumuz garantili model ismini kullanıyoruz:
    model = genai.GenerativeModel('models/gemini-flash-latest')
    

def get_topics():
    """İnsan verisinden rastgele kelimeler alarak konu üretir"""
    try:
        df = pd.read_csv(INSAN_VERISI_DOSYASI)
        ornekler = df['text'].sample(n=50).tolist()
        konular = ["Computer Science", "Artificial Intelligence", "Machine Learning", "Cyber Security"]
        for metin in ornekler:
            konular.append(metin[:50]) 
        return konular
    except:
        return ["Computer Science", "Artificial Intelligence", "Software Engineering"]

def generate_ai_data():
    print(f"--- AI Veri Üretimi Başlıyor (Hedef: {HEDEF_SAYI}) ---")
    print(f"Kullanılan Model: models/gemini-flash-latest")
    
    if os.path.exists(DOSYA_ADI):
        df_mevcut = pd.read_csv(DOSYA_ADI)
        ai_data = df_mevcut.to_dict('records')
        print(f"Mevcut dosya bulundu. {len(ai_data)} veriden devam ediliyor...")
    else:
        ai_data = []

    konu_listesi = get_topics()

    while len(ai_data) < HEDEF_SAYI:
        try:
            konu = random.choice(konu_listesi)
            
            # İstek gönder
            prompt = f"Write a strictly academic abstract for a research paper about '{konu}'. It should be technically dense, about 6-8 sentences long. Do NOT add any introduction, title or conclusion. Just the abstract text."
            
            response = model.generate_content(prompt)
            
            # Gelen cevabı temizle
            if response.text:
                text = response.text.replace("\n", " ").replace("*", "").strip()
                ai_data.append({"text": text, "label": "AI"})
                
                kalan = HEDEF_SAYI - len(ai_data)
                print(f"[{len(ai_data)}/{HEDEF_SAYI}] Üretildi. (Kalan: {kalan})")

                # Her 10 tanede bir kaydet
                if len(ai_data) % 10 == 0:
                    pd.DataFrame(ai_data).to_csv(DOSYA_ADI, index=False)
                    print(f">> Dosya güncellendi ({len(ai_data)} veri).")

                # Hız sınırı için bekleme (Flash modeli hızlıdır ama yine de 4 sn bekleyelim garanti olsun)
                time.sleep(4) 
            else:
                print("Boş cevap geldi, tekrar deneniyor...")

        except Exception as e:
            print(f"Hata oluştu (1 dk bekleniyor...): {e}")
            time.sleep(60)

    pd.DataFrame(ai_data).to_csv(DOSYA_ADI, index=False)
    print(f"\nTEBRİKLER! {HEDEF_SAYI} adet AI verisi tamamlandı.")

if __name__ == "__main__":
    generate_ai_data()
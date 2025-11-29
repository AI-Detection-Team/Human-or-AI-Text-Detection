import pandas as pd
import re
 #Veri temizleme işlemi yapıldı
def clean_text(text):
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^\w\s]', '', text)
    return text.strip()

def prepare_data():
    print("Veriler birleştiriliyor...")
    try:
        df_human = pd.read_csv("human_data.csv")
        df_ai = pd.read_csv("ai_data.csv")
    except FileNotFoundError:
        print("HATA: csv dosyaları yok. Lütfen 'git pull' yapın.")
        return

    df_human['label'] = 'Human'
    df_ai['label'] = 'AI'

    df_final = pd.concat([df_human, df_ai], ignore_index=True)
    df_final['text'] = df_final['text'].apply(clean_text)
    
    df_final = df_final.dropna(subset=['text'])
    df_final = df_final[df_final['text'] != ""]
    df_final = df_final.sample(frac=1, random_state=42).reset_index(drop=True)

    df_final.to_csv("dataset_final.csv", index=False)
    print(f"BAŞARILI! {len(df_final)} satır veri kaydedildi.")

if __name__ == "__main__":
    prepare_data()
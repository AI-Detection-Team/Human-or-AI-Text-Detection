import arxiv
import pandas as pd

def fetch_human_data():
    print("ArXiv üzerinden İnsan yazımı makaleler çekiliyor... (Bu işlem biraz sürebilir)")

    # Bilgisayar Bilimleri (CS) alanında yapay zeka (AI) makaleleri
    client = arxiv.Client()
    search = arxiv.Search(
        query = "cat:cs.AI",
        max_results = 4000,  # Hedef 4000 makale
        sort_by = arxiv.SortCriterion.SubmittedDate
    )

    data = []

    # Sonuçları çekiyoruz
    results = client.results(search)

    count = 0
    try:
        for r in results:
            # Özet metnini al (summary) ve satır sonlarını temizle
            summary = r.summary.replace("\n", " ")

            data.append({
                "text": summary,
                "label": "Human"
            })

            count += 1
            if count % 100 == 0:
                print(f"{count} adet veri çekildi...")

    except Exception as e:
        print(f"Bir hata oluştu veya limit doldu: {e}")

    # DataFrame'e çevir ve kaydet
    df = pd.DataFrame(data)
    df.to_csv("human_data.csv", index=False)
    print(f"\nİşlem Tamam! Toplam {len(df)} satır 'human_data.csv' dosyasına kaydedildi.")

if __name__ == "__main__":
    fetch_human_data()

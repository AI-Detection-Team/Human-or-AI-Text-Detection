import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
#Modeller eğitildi
def train_models():
    print("Modeller eğitiliyor... (Lütfen bekleyin)")
    try:
        df = pd.read_csv("dataset_final.csv")
    except:
        print("Veri bulunamadı! Önce data_preprocessing.py çalıştırın.")
        return

    X = df['text'].fillna('')
    y = df['label']

    # TF-IDF (Metni sayıya çevirme)
    print("Vektörleştirme yapılıyor...")
    vectorizer = TfidfVectorizer(max_features=5000)
    X_vec = vectorizer.fit_transform(X)

    # Eğitim/Test Ayrımı
    X_train, X_test, y_train, y_test = train_test_split(X_vec, y, test_size=0.2, random_state=42)

    # 1. Naive Bayes
    print("- Naive Bayes eğitiliyor...")
    nb = MultinomialNB()
    nb.fit(X_train, y_train)
    print(f"  Başarı: %{accuracy_score(y_test, nb.predict(X_test))*100:.2f}")

    # 2. Logistic Regression
    print("- Logistic Regression eğitiliyor...")
    lr = LogisticRegression(max_iter=1000)
    lr.fit(X_train, y_train)
    print(f"  Başarı: %{accuracy_score(y_test, lr.predict(X_test))*100:.2f}")

    # 3. Random Forest
    print("- Random Forest eğitiliyor...")
    rf = RandomForestClassifier(n_estimators=50, random_state=42)
    rf.fit(X_train, y_train)
    print(f"  Başarı: %{accuracy_score(y_test, rf.predict(X_test))*100:.2f}")

    # Kaydetme
    print("Modeller kaydediliyor...")
    joblib.dump(nb, 'model_nb.pkl')
    joblib.dump(lr, 'model_lr.pkl')
    joblib.dump(rf, 'model_rf.pkl')
    joblib.dump(vectorizer, 'vectorizer.pkl')
    print("Tamamlandı!")

if __name__ == "__main__":
    train_models()
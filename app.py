import streamlit as st
import joblib
import re
import os

# --- SAYFA AYARLARI ---
st.set_page_config(
    page_title="Text Origin - Analiz Aracı",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS TASARIM (Güzelleştirme + GİZLEME KODLARI) ---
st.markdown("""
<style>
    /* 1. GİZLEME KODLARI (Deploy, Menu, Footer Yok Etme) */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    [data-testid="stToolbar"] {visibility: hidden; display: none;}
    
    /* Üst boşluğu azaltma (Header gidince oluşan boşluk için) */
    .block-container {
        padding-top: 1rem;
    }

    /* 2. MEVCUT TASARIM KODLARI (Sizin kodunuz) */
    /* Ana başlık */
    .main-title {
        font-size: 3rem;
        font-family: 'Helvetica Neue', sans-serif;
        font-weight: 700;
        color: #2C3E50;
        text-align: center;
        margin-bottom: 20px;
    }
    /* Alt başlık */
    .sub-title {
        font-size: 1.2rem;
        color: #7F8C8D;
        text-align: center;
        margin-bottom: 40px;
    }
    /* Buton */
    .stButton>button {
        background-color: #6C63FF;
        color: white;
        border-radius: 25px;
        padding: 10px 24px;
        border: none;
        font-weight: bold;
        width: 100%;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #5a52d5;
        transform: scale(1.02);
    }
    /* Sonuç Kartları */
    .result-box {
        padding: 15px;
        border-radius: 15px;
        background-color: #26273B;
        border: 1px solid #e9ecef;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        margin-top: 10px;
    }
</style>
""", unsafe_allow_html=True)

# --- 1. MODELLERİ YÜKLEME ---
@st.cache_resource
def load_models():
    try:
        vec = joblib.load('vectorizer.pkl')
        nb = joblib.load('model_nb.pkl')
        lr = joblib.load('model_lr.pkl')
        rf = joblib.load('model_rf.pkl')
        return vec, nb, lr, rf
    except Exception as e:
        return None, None, None, None

vectorizer, nb_model, lr_model, rf_model = load_models()

# --- 2. TEMİZLEME FONKSİYONU ---
def clean_text(text):
    text = text.lower()
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^\w\s]', '', text)
    return text.strip()

# --- 3. YAN MENÜ (SOL PANEL) ---
with st.sidebar:
    # --- LOGO ALANI ---
    if os.path.exists("images/logo.png"):
        st.image("images/logo.png", use_container_width=True)
    else:
        st.header("🕵️ Human or AI")
        
    st.markdown("---")
    st.subheader("Geliştirici Ekip")

    # --- EKİP ÜYELERİ (Görselli - Mesleksiz) ---
    
    # 1. Kişi (Fatma)
    col_img, col_txt = st.columns([1, 2])
    with col_img:
        if os.path.exists("images/profil1.png"):
            st.image("images/profil1.png", width=60)
    with col_txt:
        st.markdown("<br>**Fatma Aytaş**", unsafe_allow_html=True)

    # 2. Kişi (Pınar)
    col_img, col_txt = st.columns([1, 2])
    with col_img:
        if os.path.exists("images/profil2.png"):
            st.image("images/profil2.png", width=60)
    with col_txt:
        st.markdown("<br>**Pınar Eray**", unsafe_allow_html=True)

    # 3. Kişi (Yağmur)
    col_img, col_txt = st.columns([1, 2])
    with col_img:
        if os.path.exists("images/profil3.png"):
            st.image("images/profil3.png", width=60)
    with col_txt:
        st.markdown("<br>**Yağmur Sultan Ekin**", unsafe_allow_html=True)

    st.markdown("---")
    st.info("💡 **Proje Hakkında:**\nBu yazılım, akademik makale özetlerinin Yapay Zeka mı yoksa İnsan mı tarafından yazıldığını tespit eder.")
    st.caption("v1.0.5 - Final Release")

# --- 4. ANA EKRAN ---

st.markdown('<div class="main-title">Makale Köken Analizi</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Yapay Zeka (AI) ve İnsan Yazımı metinleri ayırt eden akıllı asistan.</div>', unsafe_allow_html=True)

if vectorizer is None:
    st.error("⚠️ Model dosyaları (.pkl) bulunamadı! Lütfen eğitimi tamamlayın.")
    st.stop()

# Giriş Alanı
user_input = st.text_area("✍️ Analiz edilecek metni buraya yapıştırın:", height=150, placeholder="Örnek: This study explores the impact of machine learning...")

if st.button("Analizi Başlat"):
    if not user_input:
        st.warning("Lütfen bir metin girin.")
    else:
        cleaned_text = clean_text(user_input)
        vectorized_text = vectorizer.transform([cleaned_text])

        st.markdown("---")
        
        # --- DEĞİŞİKLİK BURADA: Başlığı ortaladık ve ikonu kaldırdık ---
        st.markdown("<h3 style='text-align: center; color: #2C3E50; margin-bottom: 30px;'>Algoritma Sonuçları</h3>", unsafe_allow_html=True)
        
        c1, c2, c3 = st.columns(3)

        # Sonuç Gösterim Fonksiyonu
        def show_result(col, model_name, model, img_path):
            with col:
                # İkon Gösterimi
                if os.path.exists(img_path):
                    st.image(img_path, width=80) 
                
                # Tahmin
                prob = model.predict_proba(vectorized_text)[0]
                classes = list(model.classes_)
                if 'AI' in classes:
                    ai_score = prob[classes.index('AI')]
                else:
                    ai_score = prob[0]
                
                prediction = model.predict(vectorized_text)[0]
                
                if prediction == 'AI':
                    res_color = "#6C63FF" # Mor
                    label_text = "Yapay Zeka"
                else:
                    res_color = "#2ecc71" # Yeşil
                    label_text = "İnsan Yazımı"

                # Sonuç Kartı HTML
                st.markdown(f"""
                <div class="result-box">
                    <h3 style="color: #2C3E50; margin:0; font-size:18px;">{model_name}</h3>
                    <h2 style="color: {res_color}; font-size: 22px; margin: 10px 0;">{label_text}</h2>
                    <p style="color: #95a5a6; font-size: 12px; margin-bottom:5px;">AI Olasılığı</p>
                    <div style="background-color: #e0e0e0; border-radius: 10px; width: 100%; height: 8px;">
                        <div style="background-color: {res_color}; width: {int(ai_score*100)}%; height: 100%; border-radius: 10px;"></div>
                    </div>
                    <p style="margin-top:5px; font-weight:bold;">%{ai_score*100:.1f}</p>
                </div>
                """, unsafe_allow_html=True)

        # Kartları Çağır
        show_result(c1, "Naive Bayes", nb_model, "images/naive.png")
        show_result(c2, "Logistic Reg.", lr_model, "images/logistic.png")
        show_result(c3, "Random Forest", rf_model, "images/forest.png")
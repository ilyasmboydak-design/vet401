import streamlit as st
import json
import re
import os

# Page Config
st.set_page_config(
    page_title="VET401 Akıllı Anamnez & Bulgu Sorgu Konsolu (27 Vaka)",
    page_icon="🐄",
    layout="wide",
)

# Custom Styling
st.markdown("""
    <style>
    .main-title {
        color: #1F4E79;
        font-family: 'Arial', sans-serif;
        font-weight: bold;
        text-align: center;
        margin-bottom: 2px;
    }
    .sub-title {
        color: #595959;
        font-family: 'Arial', sans-serif;
        font-style: italic;
        text-align: center;
        font-size: 15px;
        margin-bottom: 20px;
    }
    .vaka-box {
        background-color: #EBF1F5;
        border: 2px solid #1F4E79;
        padding: 15px 20px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .vaka-header {
        background: linear-gradient(90deg, #1F4E79 0%, #2F5597 100%);
        color: white;
        padding: 12px 20px;
        border-radius: 8px;
        font-size: 18px;
        font-weight: bold;
        margin-bottom: 15px;
    }
    .card-found {
        background-color: #F2F4F8;
        border-left: 6px solid #1F4E79;
        padding: 14px 18px;
        border-radius: 6px;
        margin-bottom: 12px;
        box-shadow: 1px 1px 5px rgba(0,0,0,0.05);
    }
    .card-title {
        font-weight: bold;
        color: #1F4E79;
        font-size: 15px;
        margin-bottom: 4px;
    }
    .card-content {
        font-size: 15px;
        color: #262626;
        line-height: 1.5;
    }
    .badge-category {
        background-color: #D9E1F2;
        color: #1F4E79;
        padding: 3px 10px;
        border-radius: 4px;
        font-size: 13px;
        font-weight: bold;
    }
    .instructor-section {
        background-color: #FFF2CC;
        border-left: 5px solid #D6B656;
        padding: 10px 14px;
        border-radius: 5px;
        margin-bottom: 10px;
        font-size: 13px;
    }
    </style>
""", unsafe_allow_html=True)

# Smart Multi-Directory Case-Insensitive Image Resolver
def get_smart_image(target_name):
    if not target_name:
        return None
    
    clean_target = re.sub(r'[^a-zA-Z0-9]', '', str(target_name)).lower()
    
    search_dirs = [
        ".",
        "gorseller_2",
        "gorseller",
        "artifacts",
        "images",
        "/workspace/artifacts",
        "/workspace/out",
        "/workspace/scratch"
    ]
    
    for s_dir in search_dirs:
        if os.path.exists(s_dir):
            try:
                for fname in os.listdir(s_dir):
                    fpath = os.path.join(s_dir, fname)
                    if os.path.isfile(fpath):
                        clean_fname = re.sub(r'[^a-zA-Z0-9]', '', os.path.splitext(fname)[0]).lower()
                        if clean_fname == clean_target:
                            return fpath
            except Exception:
                pass
    return None

# Load Case Database JSON
@st.cache_data
def load_database():
    json_paths = [
        "vaka_veritabani.json",
        "artifacts/vaka_veritabani.json",
        "/workspace/artifacts/vaka_veritabani.json",
        "/workspace/out/vaka_veritabani.json",
        "/workspace/scratch/vaka_veritabani.json"
    ]
    for path in json_paths:
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                pass
    return {}

CASES = load_database()

# Header
st.markdown("<h1 class='main-title'>🐄 VET401 Akıllı Anamnez & Bulgu Sorgu Konsolu</h1>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>Çukurova Üniversitesi Veteriner Fakültesi — 27 Klinik Vaka Bankası (Ders I & II)</div>", unsafe_allow_html=True)

if not CASES:
    st.error("⚠️  yüklenemedi! Lütfen dosyanın klasörde olduğunu kontrol ediniz.")
    st.stop()

# Filter Module Options
st.markdown("<div class='vaka-box'>", unsafe_allow_html=True)
col_mod, col_case = st.columns([1, 2])

with col_mod:
    module_filter = st.selectbox(
        "📂 Ders / Modül Seçiniz:",
        options=["Tüm Vakalar (27 Vaka)", "Ders I — Dolaşım & Deri (12 Vaka)", "Ders II — Kan, Parazit & Deri (15 Vaka)"]
    )

if "Ders I" in module_filter:
    filtered_cases = [k for k in CASES.keys() if k.startswith("Vaka ") and k.split()[1] in ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L"]]
elif "Ders II" in module_filter:
    filtered_cases = [k for k in CASES.keys() if k.startswith("Vaka ") and k.split()[1].isdigit()]
else:
    filtered_cases = list(CASES.keys())

with col_case:
    selected_case_name = st.selectbox(
        "🔍 İncelemek İstediğiniz Vakayı Seçiniz:",
        options=filtered_cases,
        index=0
    )
st.markdown("</div>", unsafe_allow_html=True)

active_case = CASES[selected_case_name]

# Session state initialization for question history per case
if "history" not in st.session_state:
    st.session_state.history = {}

if selected_case_name not in st.session_state.history:
    st.session_state.history[selected_case_name] = []

# Case Complaint Header (Farmer Perspective - No Hocam)
st.markdown(f"<div class='vaka-header'>📋 {selected_case_name} — İlk Başvuru Şikayeti</div>", unsafe_allow_html=True)
st.info(f"**🗣️ Yetiştiricinin İfadesi:** {active_case['sikayet']}")

# Macroscopic Image Section if available
if "makroskopik_gorsel" in active_case:
    mg = active_case["makroskopik_gorsel"]
    file_target = mg.get("file", "")
    img_path = get_smart_image(file_target)
    
    st.markdown("### 📸 Klinik Makroskopik Lezyon Görseli")
    if img_path:
        st.image(img_path, caption=f"{mg.get('fig', '')} — {mg.get('title', '')}", use_container_width=True)
    else:
        st.caption(f"**{mg.get('fig', '')} — {mg.get('title', '')}**")
        st.write(mg.get("desc", ""))
        with st.expander("🖼️ Görsel Görünmüyorsa / Fotoğraf Yüklemek İçin Tıklayınız"):
            uploaded_file = st.file_uploader("📷 Fotoğraf Dosyası Seçiniz (.jpg / .png):", type=["jpg", "jpeg", "png"], key=f"up_macro_{active_case['kod']}")
            if uploaded_file is not None:
                st.image(uploaded_file, caption="Yüklenen Fotoğraf", use_container_width=True)

st.markdown("---")

# QUESTION INPUT SECTION
st.markdown("### 💬 Sorunuzu veya İncelemek İstediğiniz Muayeneyi Yazınız:")

def match_query(user_text, categories_dict):
    text_clean = user_text.lower().strip()
    text_clean = text_clean.replace("ı", "i").replace("ğ", "g").replace("ü", "u").replace("ş", "s").replace("ö", "o").replace("ç", "c")
    
    micro_keywords = ["mikroskop", "frotı", "froti", "kazıntı", "lam", "biyopsi", "giemsa", "koh", "spiroket", "akar", "uyuz", "inklüzyon"]
    if any(k in text_clean for k in micro_keywords):
        for k_cat in ["GORUNTULEME_MIKROBIYOLOJI", "MIKROSKOPI_KAZINTI"]:
            if k_cat in categories_dict:
                return [k_cat]

    matched_cats = []
    for cat_key, cat_info in categories_dict.items():
        for kw in cat_info.get("keywords", []):
            kw_clean = kw.lower().replace("ı", "i").replace("ğ", "g").replace("ü", "u").replace("ş", "s").replace("ö", "o").replace("ç", "c")
            if re.search(r'' + re.escape(kw_clean), text_clean) or kw_clean in text_clean:
                matched_cats.append(cat_key)
                break
    return matched_cats

col_input, col_button = st.columns([4, 1])

with col_input:
    user_query = st.text_input(
        "Sorunuzu Buraya Yazınız:",
        key="query_input",
        placeholder="Örn: İştah durumu nasıl?, İdrar tahlili sonucu nedir?, Deri kazıntısı yapalım, Kan gazı sonucu..."
    )

with col_button:
    st.markdown("<div style='height:28px;'></div>", unsafe_allow_html=True)
    submit_btn = st.button("🔎 Sor ve Sorgula", type="primary", use_container_width=True)

if submit_btn and user_query:
    matches = match_query(user_query, active_case["categories"])
    if matches:
        new_disc = 0
        for cat_key in matches:
            cat_data = active_case["categories"][cat_key]
            already_in = any(item["cat_key"] == cat_key for item in st.session_state.history[selected_case_name])
            if not already_in:
                item_dict = {
                    "cat_key": cat_key,
                    "query": user_query,
                    "title": cat_data.get("name", "Bulgu"),
                    "content": cat_data.get("content", "")
                }
                if "gorsel" in cat_data:
                    item_dict["gorsel"] = cat_data["gorsel"]
                st.session_state.history[selected_case_name].append(item_dict)
                new_disc += 1
        if new_disc > 0:
            st.success(f"🎉 {new_disc} yeni klinik bulgu / tahlil verisi açığa çıkarıldı!")
    else:
        st.warning("⚠️ Eşleşen bilgi bulunamadı. Lütfen sorunuzu farklı kelimelerle yazınız.")

# Display Discovered Information
st.markdown("---")
st.markdown(f"### 📂 Keşfedilen Klinik İpuçları ve Muayene Bulguları ({len(st.session_state.history[selected_case_name])} Bilgi Açıldı)")

if st.session_state.history[selected_case_name]:
    if st.button("🗑️ Bu Vakanın Sorgu Geçmişini Temizle"):
        st.session_state.history[selected_case_name] = []
        st.rerun()

    for item in reversed(st.session_state.history[selected_case_name]):
        st.markdown(f"""
            <div class='card-found'>
                <div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;'>
                    <span class='badge-category'>{item['title']}</span>
                    <span style='font-size:12px; color:#7F7F7F;'>Sorulan Soru: "{item['query']}"</span>
                </div>
                <div class='card-content'><b>🩺 Bulgu / Tahlil Verisi:</b> {item['content']}</div>
            </div>
        """, unsafe_allow_html=True)
        
        if "gorsel" in item:
            g = item["gorsel"]
            g_target = g.get("file", "")
            g_path = get_smart_image(g_target)
            st.markdown(f"#### 🔬 {g.get('title', 'Mikroskopik İnceleme')} ({g.get('fig', '')})")
            if g_path:
                st.image(g_path, caption=f"{g.get('fig', '')} — {g.get('title', '')}", use_container_width=True)
            else:
                st.write(g.get("desc", ""))
                with st.expander("🖼️ Mikroskop Görseli Yüklemek İçin Tıklayınız"):
                    up_m = st.file_uploader("📷 Fotoğraf Dosyası Seçiniz:", type=["jpg", "jpeg", "png"], key=f"up_micro_{item['cat_key']}")
                    if up_m is not None:
                        st.image(up_m, caption="Yüklenen Mikroskopik Görsel", use_container_width=True)

# Teacher Portal
with st.sidebar:
    st.markdown("### 🏛️ ÇU Veteriner Fakültesi")
    st.markdown("**VET401 İç Hastalıkları I**")
    st.markdown("---")
    st.markdown("### 🔒 Eğitmen Portalı")
    teacher_login = st.checkbox("Eğitmen Anahtar Paneli")
    if teacher_login:
        pass_code = st.text_input("Giriş Şifresi:", type="password")
        if pass_code == "vet401":
            st.success("Eğitmen Erişimi Onaylandı!")
            st.markdown(f"#### 🔑 {selected_case_name} — Gizli Eğitmen Rehberi:")
            
            eb = active_case.get("egitmen_bilgisi", {})
            if "kesin_tani" in eb:
                st.markdown(f"<div class='instructor-section'><b>🎯 Kesin Tanı:</b><br>{eb['kesin_tani']}</div>", unsafe_allow_html=True)
            if "patofizyoloji" in eb:
                st.markdown(f"<div class='instructor-section'><b>🔬 Patofizyoloji:</b><br>{eb['patofizyoloji']}</div>", unsafe_allow_html=True)
            if "ayirici_tani" in eb:
                st.markdown(f"<div class='instructor-section'><b>⚖️ Ayırıcı Tanı:</b><br>{eb['ayirici_tani']}</div>", unsafe_allow_html=True)
            if "tedavi_protokolu" in eb:
                st.markdown(f"<div class='instructor-section'><b>💊 Sağaltım Protokolü:</b><br>{eb['tedavi_protokolu']}</div>", unsafe_allow_html=True)
            if "koruma_biyogüvenlik" in eb:
                st.markdown(f"<div class='instructor-section'><b>🛡️ Sürü Sağlığı & Biyogüvenlik:</b><br>{eb['koruma_biyogüvenlik']}</div>", unsafe_allow_html=True)
            
            st.markdown("#### 📊 Vakanın Tüm Tahlil & Muayene Bulguları:")
            for ck, cv in active_case["categories"].items():
                st.markdown(f"**• {cv.get('name', ck)}:** {cv.get('content', '')}")
        elif pass_code:
            st.error("Hatalı Şifre!")

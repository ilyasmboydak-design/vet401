import streamlit as st
import json
import re
import os
import glob

# Page Config
st.set_page_config(
    page_title="VET401 Akıllı Anamnez & Bulgu Sorgu Konsolu",
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

# Helper function to find images dynamically
def find_gorsel_path(file_path):
    if not file_path:
        return None
    if os.path.exists(file_path):
        return file_path
    
    base_name = os.path.basename(file_path)
    name_no_ext, ext = os.path.splitext(base_name)
    
    possible_names = [
        base_name,
        f"{name_no_ext}.png",
        f"{name_no_ext}.jpg",
        f"{name_no_ext}.jpeg",
    ]
    
    script_dir = os.path.dirname(os.path.abspath(__file__)) if '__file__' in globals() else os.getcwd()
    search_dirs = [
        ".",
        "gorseller",
        "artifacts",
        script_dir,
        os.path.join(script_dir, "gorseller"),
        "/workspace/artifacts",
        "/workspace/out",
        "/workspace/scratch"
    ]
    
    for s_dir in search_dirs:
        if not os.path.exists(s_dir):
            continue
        for p_name in possible_names:
            full_p = os.path.join(s_dir, p_name)
            if os.path.exists(full_p):
                return full_p
    return None

# Find all JSON database files in the workspace / folder
def get_available_json_files():
    script_dir = os.path.dirname(os.path.abspath(__file__)) if '__file__' in globals() else os.getcwd()
    search_locations = [
        os.getcwd(),
        script_dir,
        os.path.join(os.getcwd(), "artifacts"),
        "/workspace/artifacts",
        "/workspace/scratch"
    ]
    
    found_files = {}
    for loc in search_locations:
        if not os.path.exists(loc):
            continue
        for fpath in glob.glob(os.path.join(loc, "*.json")):
            fname = os.path.basename(fpath)
            # Filter out non-case json files
            if fname in ["package.json", "tsconfig.json"]:
                continue
            if fname not in found_files:
                found_files[fname] = fpath
                
    # Sort files putting vaka_veritabani_2.json or modul_1 first
    sorted_names = sorted(list(found_files.keys()), key=lambda x: (
        0 if "vaka_veritabani_2" in x else (1 if "modul" in x else 2), x
    ))
    return {name: found_files[name] for name in sorted_names}

JSON_FILES = get_available_json_files()

# App Header
st.markdown("<h1 class='main-title'>🐄 VET401 Akıllı Anamnez & Bulgu Sorgu Konsolu</h1>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>Çukurova Üniversitesi Veteriner Fakültesi — İç Hastalıkları Vaka Bankası</div>", unsafe_allow_html=True)

if not JSON_FILES:
    st.error("⚠️ Hiçbir `.json` vaka veritabanı dosyası bulunamadı! Lütfen vakalarınızı içeren JSON dosyasını uygulamanın olduğu klasöre yükleyiniz.")
    st.stop()

# FILE AND CASE SELECTION AREA
st.markdown("<div class='vaka-box'>", unsafe_allow_html=True)
col_file, col_case = st.columns([1, 2])

with col_file:
    selected_file_name = st.selectbox(
        "📁 Yüklenecek JSON Veri Tabanı:",
        options=list(JSON_FILES.keys()),
        index=0
    )

# Load selected JSON file
selected_json_path = JSON_FILES[selected_file_name]
try:
    with open(selected_json_path, "r", encoding="utf-8") as f:
        CASES = json.load(f)
except Exception as e:
    st.error(f"Seçilen JSON dosyası okunamadı ({selected_file_name}): {e}")
    st.stop()

if not isinstance(CASES, dict) or not CASES:
    st.warning("⚠️ Seçilen JSON dosyası geçerli vaka içermiyor.")
    st.stop()

with col_case:
    selected_case_name = st.selectbox(
        "🔍 İncelemek İstediğiniz Vakayı Seçiniz:",
        options=list(CASES.keys()),
        index=0
    )
st.markdown("</div>", unsafe_allow_html=True)

active_case = CASES[selected_case_name]

# Session state initialization for question history per case
if "history" not in st.session_state:
    st.session_state.history = {}

if selected_case_name not in st.session_state.history:
    st.session_state.history[selected_case_name] = []

# Case Complaint Header
st.markdown(f"<div class='vaka-header'>📋 {selected_case_name} — İlk Başvuru Şikayeti</div>", unsafe_allow_html=True)
st.info(f"**Hastanın Başvuru Şikayeti:** {active_case.get('sikayet', 'Şikayet metni bulunamadı.')}")

# AUTOMATIC MACROSCOPIC IMAGE DISPLAY UPON CASE SELECTION (IF PRESENT)
if "makroskopik_gorsel" in active_case and isinstance(active_case["makroskopik_gorsel"], dict):
    mg = active_case["makroskopik_gorsel"]
    st.markdown("### 📸 Klinik Makroskopik Lezyon Görseli")
    
    img_path = find_gorsel_path(mg.get("file"))
    if img_path:
        st.image(img_path, caption=f"{mg.get('fig', 'Şekil')} - {mg.get('title', '')}", use_column_width=True)
    else:
        st.caption(f"**{mg.get('fig', 'Şekil')} — {mg.get('title', '')}**")
        if mg.get("desc"):
            st.write(mg["desc"])

st.markdown("---")

# QUESTION INPUT SECTION
st.markdown("### 💬 Sorunuzu veya İncelemek İstediğiniz Muayeneyi Yazınız:")

def match_query(user_text, categories_dict):
    text_clean = user_text.lower().strip()
    text_clean = text_clean.replace("ı", "i").replace("ğ", "g").replace("ü", "u").replace("ş", "s").replace("ö", "o").replace("ç", "c")
    
    # STRICT RULE: Mikroskop / Froti / Kazıntı / Ultrason queries trigger GORUNTULEME_MIKROBIYOLOJI
    micro_keywords = [
        "mikroskop", "kazinti", "froti", "lam", "lama", "akar", "akarine",
        "biyopsi", "koilosit", "inkluzyon", "spirakulum", "stigmata", "gram",
        "giemsa", "rhodanine", "coombs", "dark-field", "karanlik saha",
        "parazit", "merozoit", "szont", "koch", "spiroket", "neoplastik", "ultrason", "usg", "liptak"
    ]
    if any(mkw in text_clean for mkw in micro_keywords):
        if "GORUNTULEME_MIKROBIYOLOJI" in categories_dict:
            return ["GORUNTULEME_MIKROBIYOLOJI"]

    matched_cats = []
    for cat_key, cat_info in categories_dict.items():
        if not isinstance(cat_info, dict):
            continue
        for kw in cat_info.get("keywords", []):
            kw_clean = str(kw).lower().replace("ı", "i").replace("ğ", "g").replace("ü", "u").replace("ş", "s").replace("ö", "o").replace("ç", "c")
            if re.search(r'\b' + re.escape(kw_clean), text_clean) or kw_clean in text_clean:
                matched_cats.append(cat_key)
                break
    return matched_cats

col_input, col_button = st.columns([4, 1])

with col_input:
    user_query = st.text_input(
        "Sorunuzu Buraya Yazınız:",
        key="query_input",
        placeholder="Örn: Ateşi kaç derece?, Rasyonunda ne var?, Biyokimya tahlili istiyorum, Kan gazı bakabilir miyiz..."
    )

with col_button:
    st.markdown("<div style='height:28px;'></div>", unsafe_allow_html=True)
    submit_btn = st.button("🔎 Sor ve Sorgula", type="primary", use_container_width=True)

if submit_btn and user_query:
    cats_dict = active_case.get("categories", {})
    matches = match_query(user_query, cats_dict)
    if matches:
        new_disc = 0
        for cat_key in matches:
            cat_data = cats_dict[cat_key]
            already_in = any(item["cat_key"] == cat_key for item in st.session_state.history[selected_case_name])
            if not already_in:
                item_dict = {
                    "cat_key": cat_key,
                    "query": user_query,
                    "title": cat_data.get("name", cat_key),
                    "content": cat_data.get("content", "")
                }
                if "gorsel" in cat_data:
                    item_dict["gorsel"] = cat_data["gorsel"]
                st.session_state.history[selected_case_name].append(item_dict)
                new_disc += 1
        if new_disc > 0:
            st.success(f"🎉 {new_disc} yeni klinik bulgu / bilgi açığa çıkarıldı!")
    else:
        st.warning("⚠️ Eşleşen bilgi bulunamadı. Lütfen sorunuzu farklı kelimelerle yazınız.")

# DISPLAY DISCOVERED INFORMATION
st.markdown("---")
current_history = st.session_state.history.get(selected_case_name, [])
st.markdown(f"### 📂 Keşfedilen Klinik İpuçları ve Muayene Bulguları ({len(current_history)} Bilgi Açıldı)")

if current_history:
    for item in reversed(current_history):
        st.markdown(f"""
            <div class='card-found'>
                <div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;'>
                    <span class='badge-category'>{item['title']}</span>
                    <span style='font-size:12px; color:#7F7F7F;'>Sorulan Soru: "{item['query']}"</span>
                </div>
                <div class='card-content'><b>🩺 Bulgu / Öykü:</b> {item['content']}</div>
            </div>
        """, unsafe_allow_html=True)
        
        if "gorsel" in item and isinstance(item["gorsel"], dict):
            g = item["gorsel"]
            st.markdown(f"#### 🔬 {g.get('title', '')} ({g.get('fig', '')})")
            
            micro_img_path = find_gorsel_path(g.get("file"))
            if micro_img_path:
                st.image(micro_img_path, caption=f"{g.get('fig', '')} - {g.get('title', '')}", use_column_width=True)
            elif g.get("desc"):
                st.write(g["desc"])

    if st.button("🗑️ Bu Vakanın Sorgu Geçmişini Temizle"):
        st.session_state.history[selected_case_name] = []
        st.rerun()

# SIDEBAR: STRICTLY FOR INSTRUCTOR PORTAL
with st.sidebar:
    st.markdown("### 🏛️ ÇU Veteriner Fakültesi")
    st.markdown("**VET401 İç Hastalıkları I**")
    st.markdown("---")
    st.markdown("### 🔒 Eğitmen Portalı")
    st.caption("Eğitmenler için teşhis, patofizyoloji, ayırıcı tanı ve tam tedavi rehberi.")
    
    teacher_login = st.checkbox("Eğitmen Anahtar Paneli", key="teacher_login")
    if teacher_login:
        pass_code = st.text_input("Giriş Şifresi:", type="password", key="pass_code")
        if pass_code == "vet401":
            st.success("Eğitmen Erişimi Onaylandı!")
            
            eb = active_case.get("egitmen_bilgisi", {})
            
            st.markdown(f"### 📋 {selected_case_name}")
            
            if isinstance(eb, dict):
                if "kesin_tani" in eb:
                    st.markdown("<div class='instructor-section'><b>🎯 Kesin Tanı:</b><br>" + eb["kesin_tani"] + "</div>", unsafe_allow_html=True)
                if "patofizyoloji" in eb:
                    st.markdown("<div class='instructor-section'><b>🔬 Patofizyoloji:</b><br>" + eb["patofizyoloji"] + "</div>", unsafe_allow_html=True)
                if "ayirici_tani" in eb:
                    st.markdown("<div class='instructor-section'><b>⚖️ Ayırıcı Tanı Kriterleri:</b><br>" + eb["ayirici_tani"] + "</div>", unsafe_allow_html=True)
                if "tedavi_protokolu" in eb:
                    st.markdown("<div class='instructor-section'><b>💊 Tam Tedavi Protokolü:</b><br>" + eb["tedavi_protokolu"] + "</div>", unsafe_allow_html=True)
                if "koruma_biyogüvenlik" in eb:
                    st.markdown("<div class='instructor-section'><b>🛡️ Sürü Sağlığı & Biyogüvenlik:</b><br>" + eb["koruma_biyogüvenlik"] + "</div>", unsafe_allow_html=True)
            elif isinstance(eb, str):
                st.markdown("<div class='instructor-section'><b>📋 Eğitmen Notu:</b><br>" + eb + "</div>", unsafe_allow_html=True)
                
            st.markdown("#### 🔑 Bu Vakanın Gizli Tüm Bulguları:")
            cats_dict = active_case.get("categories", {})
            for ck, cv in cats_dict.items():
                if isinstance(cv, dict):
                    st.markdown(f"**• {cv.get('name', ck)}:** {cv.get('content', '')}")
        elif pass_code:
            st.error("Hatalı Şifre!")

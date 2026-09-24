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

# Helper function to find images dynamically without wild false matches
def find_gorsel_path(file_path):
    if not file_path:
        return None
    
    # Direct check
    if os.path.exists(file_path) and os.path.isfile(file_path):
        return file_path
    
    # Check filename variations
    base_name = os.path.basename(file_path)
    name_no_ext, ext = os.path.splitext(base_name)
    
    possible_names = [file_path, base_name]
    if ext:
        possible_names.append(f"{name_no_ext}{ext.lower()}")
        possible_names.append(f"{name_no_ext}{ext.upper()}")
    else:
        for e in [".png", ".jpg", ".jpeg", ".webp", ".PNG", ".JPG", ".JPEG"]:
            possible_names.append(f"{name_no_ext}{e}")
            
    search_dirs = [
        ".",
        "gorseller",
        "gorseller_2",
        "artifacts",
        "/workspace/artifacts",
        "/workspace/out",
        "/workspace/scratch"
    ]
    
    for s_dir in search_dirs:
        for p_name in possible_names:
            full_p = os.path.join(s_dir, p_name)
            if os.path.exists(full_p) and os.path.isfile(full_p):
                return full_p
                
    return None

# Load Case Database JSON
@st.cache_data
def load_database():
    json_paths = [
        "vaka_veritabani.json",
        "artifacts/vaka_veritabani.json",
        "/workspace/artifacts/vaka_veritabani.json",
        "/workspace/scratch/vaka_veritabani.json"
    ]
    for path in json_paths:
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                st.error(f"Veri tabanı okuma hatası ({path}): {e}")
    return {}

CASES = load_database()

# App Header
st.markdown("<h1 class='main-title'>🐄 VET401 Akıllı Anamnez & Bulgu Sorgu Konsolu</h1>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>Çukurova Üniversitesi Veteriner Fakültesi — Bütünleşik 27 Vakalık Klinik Banka</div>", unsafe_allow_html=True)

if not CASES:
    st.error("⚠️ `vaka_veritabani.json` veri tabanı dosyası bulunamadı! Lütfen JSON dosyasını uygulamanın olduğu klasöre yükleyiniz.")
    st.stop()

# MODULE FILTER AND CASE SELECTION AT THE TOP
st.markdown("<div class='vaka-box'>", unsafe_allow_html=True)
col_mod, col_case = st.columns([1, 2])

with col_mod:
    module_filter = st.selectbox(
        "📚 Ders / Modül Seçiniz:",
        options=["Tüm Vakalar (27 Vaka)", "Ders I: Dolaşım & Deri Hastalıkları (12 Vaka)", "Ders II: Kan, Vektörel & Deri Hastalıkları (15 Vaka)"],
        index=0
    )

# Filter case list based on selection
if "Ders I" in module_filter:
    filtered_cases = [k for k in CASES.keys() if k.startswith("Vaka ") and "(" in k and ("Papatya" in k or "Yonca" in k or "Zümrüt" in k or "Yiğit" in k or "Kudret" in k or "Nazar" in k or "Çiçek" in k or "Ateş" in k or "Fırtına" in k or "Şahin" in k or "Rüzgar" in k or "Poyraz" in k)]
elif "Ders II" in module_filter:
    filtered_cases = [k for k in CASES.keys() if k.startswith("Vaka ") and "(" in k and not ("Papatya" in k or "Yonca" in k or "Zümrüt" in k or "Yiğit" in k or "Kudret" in k or "Nazar" in k or "Çiçek" in k or "Ateş" in k or "Fırtına" in k or "Şahin" in k or "Rüzgar" in k or "Poyraz" in k)]
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

# Case Complaint Header
st.markdown(f"<div class='vaka-header'>📋 {selected_case_name} — İlk Başvuru Şikayeti</div>", unsafe_allow_html=True)
st.info(f"**🗣️ Yetiştiricinin İfadesi:** \"{active_case['sikayet']}\"")

# MACROSCOPIC ENTRY IMAGE DISPLAY (ONLY FOR CASES THAT HAVE A SPECIFIED IMAGE)
if "makroskopik_gorsel" in active_case:
    mg = active_case["makroskopik_gorsel"]
    st.markdown("### 📸 Klinik Makroskopik Lezyon Görseli")
    
    img_path = find_gorsel_path(mg.get("file"))
    if img_path:
        st.image(img_path, caption=f"{mg.get('fig', 'Görsel')} — {mg.get('title', '')}", use_container_width=True)
    else:
        st.caption(f"**{mg.get('fig', '')} — {mg.get('title', '')}**")
        st.write(mg.get("desc", ""))
        st.info(f"📷 *Görsel Yolu: `{mg.get('file', 'gorseller/')}` (GitHub reponuza eklendiğinde otomatik olarak burada görüntülenecektir.)*")

st.markdown("---")

# QUESTION INPUT SECTION
st.markdown("### 💬 Sorunuzu veya İncelemek İstediğiniz Muayeneyi Yazınız:")

def match_query(user_text, categories_dict):
    text_clean = user_text.lower().strip()
    text_clean = text_clean.replace("ı", "i").replace("ğ", "g").replace("ü", "u").replace("ş", "s").replace("ö", "o").replace("ç", "c")
    
    # STRICT RULE: Mikroskop / Froti / Kazıntı queries strictly trigger GORUNTULEME_MIKROBIYOLOJI
    micro_keywords = ["mikroskop", "froti", "lam", "kazinti", "biyopsi", "giemsa", "spiroket", "inkluzyon", "akar", "uyuz", "koh", "artrospor", "mantar"]
    if any(m_kw in text_clean for m_kw in micro_keywords):
        if "GORUNTULEME_MIKROBIYOLOJI" in categories_dict:
            return ["GORUNTULEME_MIKROBIYOLOJI"]
            
    matched_cats = []
    for cat_key, cat_info in categories_dict.items():
        for kw in cat_info.get("keywords", []):
            kw_clean = kw.lower().replace("ı", "i").replace("ğ", "g").replace("ü", "u").replace("ş", "s").replace("ö", "o").replace("ç", "c")
            if re.search(r'\\b' + re.escape(kw_clean), text_clean) or kw_clean in text_clean:
                matched_cats.append(cat_key)
                break
    return matched_cats

col_input, col_button = st.columns([4, 1])

with col_input:
    user_query = st.text_input(
        "Sorunuzu Buraya Yazınız:",
        key=f"query_input_{active_case.get('kod', 'case')}",
        placeholder="Örn: İştah durumu nasıl?, İdrar tahlili sonucu nedir?, Kan gazı değerleri kaç?, Deri kazıntısı..."
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
                    "title": cat_data["name"],
                    "content": cat_data["content"]
                }
                if "gorsel" in cat_data:
                    item_dict["gorsel"] = cat_data["gorsel"]
                st.session_state.history[selected_case_name].append(item_dict)
                new_disc += 1
        if new_disc > 0:
            st.success(f"🎉 {new_disc} yeni klinik bulgu / bilgi açığa çıkarıldı!")
    else:
        st.warning("⚠️ Eşleşen bilgi bulunamadı. Lütfen sorunuzu farklı kelimelerle yazınız.")

# DISPLAY DISCOVERED CLINICAL INFORMATION
st.markdown("---")
current_history = st.session_state.history[selected_case_name]
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
        
        # MICROSCOPIC IMAGE DISPLAYED ONLY WHEN TRIGGERED
        if "gorsel" in item:
            g = item["gorsel"]
            st.markdown(f"#### 🔬 {g.get('title', 'Mikroskopik İnceleme')} ({g.get('fig', '')})")
            
            g_path = find_gorsel_path(g.get("file"))
            if g_path:
                st.image(g_path, caption=f"{g.get('fig', '')} — {g.get('title', '')}", use_container_width=True)
            else:
                st.caption(f"**{g.get('fig', '')} — {g.get('title', '')}**")
                st.write(g.get("desc", ""))
                st.info(f"📷 *Mikroskopik Görsel Yolu: `{g.get('file', 'gorseller/')}` (GitHub reponuza eklendiğinde otomatik olarak görüntülenecektir.)*")

    if st.button("🗑️ Bu Vakanın Sorgu Geçmişini Temizle"):
        st.session_state.history[selected_case_name] = []
        st.rerun()

# INSTRUCTOR PORTAL IN SIDEBAR ONLY
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
            
            eg = active_case.get("egitmen_bilgisi", {})
            st.markdown(f"#### 🎯 Kesin Tanı:")
            st.warning(f"**{eg.get('kesin_tani', active_case.get('kesin_tanis', 'Tanı Belirtilmemiş'))}**")
            
            if "patofizyoloji" in eg:
                st.markdown("#### 🔬 Patofizyoloji:")
                st.info(eg["patofizyoloji"])
                
            if "ayirici_tani" in eg:
                st.markdown("#### ⚖️ Ayırıcı Tanı Kriterleri:")
                st.info(eg["ayirici_tani"])
                
            if "tedavi_protokolu" in eg:
                st.markdown("#### 💊 Tam Tedavi Protokolü:")
                st.success(eg["tedavi_protokolu"])
                
            if "koruma_biyogüvenlik" in eg:
                st.markdown("#### 🛡️ Biyogüvenlik & Koruma:")
                st.info(eg["koruma_biyogüvenlik"])
                
            st.markdown("---")
            st.markdown("#### 🔑 Bu Vakanın Tüm Gizli Verileri:")
            for ck, cv in active_case["categories"].items():
                st.markdown(f"**• {cv['name']}:** {cv['content']}")
        elif pass_code:
            st.error("Hatalı Şifre!")

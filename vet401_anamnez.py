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

# Helper function to find images dynamically across locations and extensions
def find_gorsel_path(file_path):
    if not file_path:
        return None
    
    # Direct check
    if os.path.exists(file_path):
        return file_path
    
    # Check filename variations
    base_name = os.path.basename(file_path)
    name_no_ext, ext = os.path.splitext(base_name)
    
    possible_names = [
        file_path,
        base_name,
        f"{name_no_ext}.png",
        f"{name_no_ext}.jpg",
        f"{name_no_ext}.jpeg",
        f"{name_no_ext.lower()}.png",
        f"{name_no_ext.lower()}.jpg",
        f"{name_no_ext.upper()}.png",
        f"{name_no_ext.upper()}.jpg",
        f"{name_no_ext.capitalize()}.png",
        f"{name_no_ext.capitalize()}.jpg",
    ]
    
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
            if os.path.exists(full_p):
                return full_p
                
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
                st.error(f"Veri tabanı okuma hatası ({path}): {e}")
    return {}

CASES = load_database()

# App Header
st.markdown("<h1 class='main-title'>🐄 VET401 Akıllı Anamnez & Bulgu Sorgu Konsolu</h1>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>Çukurova Üniversitesi Ceyhan Veteriner Fakültesi — Bütünleşik Klinik Vaka Bankası (27 Vaka)</div>", unsafe_allow_html=True)

if not CASES:
    st.error("⚠️ `vaka_veritabani.json` veri tabanı dosyası bulunamadı! Lütfen JSON dosyasını uygulamanın olduğu klasöre yükleyiniz.")
    st.stop()

# DERS CATEGORIZATION FOR EASY FILTERING
ders1_cases = [k for k, v in CASES.items() if v.get("ders", "").startswith("DERS I") or (k.startswith("Vaka ") and "(" in k and k[5] in "ABCDEFGHIJKL")]
ders2_cases = [k for k, v in CASES.items() if k not in ders1_cases]

# MAIN PAGE TOP: CASE SELECTION BOX
st.markdown("<div class='vaka-box'>", unsafe_allow_html=True)

col_ders, col_case = st.columns([1, 2])

with col_ders:
    selected_ders = st.selectbox(
        "📚 Klinik Ders Modülünü Seçiniz:",
        options=["Tüm Vakalar (27 Vaka)", "Ders I: Dolaşım, Deri & Üst Solunum (12 Vaka)", "Ders II: Kan, Vektörel Parazit & Organ (15 Vaka)"]
    )

if "Ders I" in selected_ders:
    filtered_options = ders1_cases
elif "Ders II" in selected_ders:
    filtered_options = ders2_cases
else:
    filtered_options = list(CASES.keys())

with col_case:
    selected_case_name = st.selectbox(
        "🔍 İncelemek İstediğiniz Vakayı Seçiniz:",
        options=filtered_options,
        index=0
    )

st.markdown("</div>", unsafe_allow_html=True)

active_case = CASES[selected_case_name]

# Session state initialization for question history per case
if "history_master" not in st.session_state:
    st.session_state.history_master = {}

if selected_case_name not in st.session_state.history_master:
    st.session_state.history_master[selected_case_name] = []

# Case Complaint Header
st.markdown(f"<div class='vaka-header'>📋 {selected_case_name} — İlk Başvuru Şikayeti & Yetiştirici İfadesi</div>", unsafe_allow_html=True)
st.info(f"**🗣️ Yetiştiricinin/Saha İfadesi:** \"{active_case['sikayet']}\"")

# AUTOMATIC MACROSCOPIC IMAGE DISPLAY UPON CASE SELECTION
if "makroskopik_gorsel" in active_case:
    mg = active_case["makroskopik_gorsel"]
    st.markdown("### 📸 Klinik Makroskopik Lezyon Görseli")
    
    img_path = find_gorsel_path(mg.get("file"))
    if img_path:
        st.image(img_path, caption=f"{mg.get('fig', 'Görsel')} - {mg.get('title', '')}", use_container_width=True)
    else:
        st.caption(f"**{mg.get('fig', 'Klinik Görsel')} — {mg.get('title', '')}**")
        st.write(mg.get("desc", ""))
        st.info(f"📷 *Görsel Yolu: `{mg.get('file', 'gorseller/')}` (GitHub reponuza yüklendiğinde otomatik olarak burada görüntülenecektir.)*")

st.markdown("---")

# QUESTION INPUT SECTION
st.markdown("### 💬 Sorunuzu veya İncelemek İstediğiniz Muayeneyi Yazınız:")

def match_query(user_text, categories_dict):
    text_clean = user_text.lower().strip()
    text_clean = text_clean.replace("ı", "i").replace("ğ", "g").replace("ü", "u").replace("ş", "s").replace("ö", "o").replace("ç", "c")
    
    # STRICT RULE: Mikroskop / Frotı / Kazıntı queries strictly trigger GORUNTULEME_MIKROBIYOLOJI
    micro_keywords = ["mikroskop", "froti", "lam", "kazinti", "biyopsi", "spiroket", "giemsa", "gram", "kulture", "ultrason", "rontgen"]
    if any(mkw in text_clean for mkw in micro_keywords):
        if "GORUNTULEME_MIKROBIYOLOJI" in categories_dict:
            return ["GORUNTULEME_MIKROBIYOLOJI"]
            
    matched_cats = []
    for cat_key, cat_info in categories_dict.items():
        for kw in cat_info["keywords"]:
            kw_clean = kw.lower().replace("ı", "i").replace("ğ", "g").replace("ü", "u").replace("ş", "s").replace("ö", "o").replace("ç", "c")
            if re.search(r'\b' + re.escape(kw_clean), text_clean) or kw_clean in text_clean:
                matched_cats.append(cat_key)
                break
    return matched_cats

col_input, col_button = st.columns([4, 1])

with col_input:
    user_query = st.text_input(
        "Sorunuzu Buraya Yazınız:",
        key="query_input_master",
        placeholder="Örn: İştahı nasıl?, Biyokimya panelini ver, Kan gazı ne durumda?, Deri kazıntısı yapalım..."
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
            already_in = any(item["cat_key"] == cat_key for item in st.session_state.history_master[selected_case_name])
            if not already_in:
                item_dict = {
                    "cat_key": cat_key,
                    "query": user_query,
                    "title": cat_data["name"],
                    "content": cat_data["content"]
                }
                if "gorsel" in cat_data:
                    item_dict["gorsel"] = cat_data["gorsel"]
                st.session_state.history_master[selected_case_name].append(item_dict)
                new_disc += 1
        if new_disc > 0:
            st.success(f"🎉 {new_disc} yeni klinik bulgu / laboratuvar verisi açığa çıkarıldı!")
    else:
        st.warning("⚠️ Eşleşen muayene bulgusu tespit edilemedi. Lütfen sorunuzu farklı anahtar kelimelerle yazınız.")

# Display Discovered Information
st.markdown("---")
current_history = st.session_state.history_master.get(selected_case_name, [])
st.markdown(f"### 📂 Keşfedilen Klinik İpuçları ve Muayene Bulguları ({len(current_history)} Bilgi Açıldı)")

if current_history:
    col_clear, _ = st.columns([1, 3])
    with col_clear:
        if st.button("🗑️ Bu Vakanın Sorgu Geçmişini Temizle", key="clear_btn"):
            st.session_state.history_master[selected_case_name] = []
            st.rerun()

    for item in reversed(current_history):
        st.markdown(f"""
            <div class='card-found'>
                <div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;'>
                    <span class='badge-category'>{item['title']}</span>
                    <span style='font-size:12px; color:#7F7F7F;'>Sorulan Soru: "{item['query']}"</span>
                </div>
                <div class='card-content'><b>🩺 Bulgu / Tahlil Sonucu:</b> {item['content']}</div>
            </div>
        """, unsafe_allow_html=True)
        
        # MICROSCOPIC / CATEGORY IMAGES DISPLAYED ONLY WHEN TRIGGERED
        if "gorsel" in item:
            g = item["gorsel"]
            st.markdown(f"#### 🔬 {g.get('title', 'Mikroskopik Görsel')} ({g.get('fig', '')})")
            
            g_path = find_gorsel_path(g.get("file"))
            if g_path:
                st.image(g_path, caption=f"{g.get('fig', '')} - {g.get('title', '')}", use_container_width=True)
            else:
                st.write(g.get("desc", ""))
                st.info(f"📷 *Mikroskopik Görsel Yolu: `{g.get('file', 'gorseller/')}` (GitHub reponuza yüklendiğinde otomatik görünecektir.)*")

# INSTRUCTOR PORTAL IN SIDEBAR
with st.sidebar:
    st.markdown("### 🏛️ ÇU Ceyhan Veteriner Fakültesi")
    st.markdown("**VET401 İç Hastalıkları I**")
    st.markdown("---")
    st.markdown("### 🔒 Eğitmen Portalı")
    teacher_login = st.checkbox("Eğitmen Anahtar Paneli")
    
    if teacher_login:
        pass_code = st.text_input("Giriş Şifresi:", type="password", key="teacher_pass")
        if pass_code == "vet401":
            st.success("🔑 Eğitmen Erişimi Onaylandı!")
            
            eg = active_case.get("egitmen_bilgisi", {})
            
            st.markdown("<div class='instructor-section'>", unsafe_allow_html=True)
            st.markdown(f"**🎯 Kesin Tanı:** {eg.get('kesin_tani', active_case.get('kesin_tanis', 'Belirtilmedi'))}")
            st.markdown("</div>", unsafe_allow_html=True)
            
            if "patofizyoloji" in eg:
                st.markdown("<div class='instructor-section'>", unsafe_allow_html=True)
                st.markdown(f"**🔬 Klinik Patofizyoloji:** {eg['patofizyoloji']}")
                st.markdown("</div>", unsafe_allow_html=True)
                
            if "ayirici_tani" in eg:
                st.markdown("<div class='instructor-section'>", unsafe_allow_html=True)
                st.markdown(f"**⚖️ Ayırıcı Tanı Kriterleri:** {eg['ayirici_tani']}")
                st.markdown("</div>", unsafe_allow_html=True)
                
            if "tedavi_protokolu" in eg:
                st.markdown("<div class='instructor-section'>", unsafe_allow_html=True)
                st.markdown(f"**💊 Sağaltım & Reçete Protokolü:** {eg['tedavi_protokolu']}")
                st.markdown("</div>", unsafe_allow_html=True)
                
            if "koruma_biyogüvenlik" in eg:
                st.markdown("<div class='instructor-section'>", unsafe_allow_html=True)
                st.markdown(f"**🛡️ Sürü Sağlığı & Biyogüvenlik:** {eg['koruma_biyogüvenlik']}")
                st.markdown("</div>", unsafe_allow_html=True)
                
            st.markdown("---")
            st.markdown("#### 🔑 Bu Vakanın Tüm Gizli Kategori Verileri:")
            for ck, cv in active_case["categories"].items():
                st.markdown(f"**• {cv['name']}:** {cv['content']}")
        elif pass_code:
            st.error("❌ Hatalı Şifre!")

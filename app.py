python
import io
import logging
import random
import urllib.parse
import pandas as pd
import requests
import streamlit as st
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

# ڕێکخستنی لاپەڕەکە بە دیزاینی مۆدێرن و پان
st.set_page_config(
    page_title="LAV LAB - Real-time Chemical Portal",
    page_icon="🧪",
    layout="wide"
)

# لۆگەر بۆ تۆمارکردنی کارەکان
logging.basicConfig(level=logging.INFO)

# ستایلکردنی لووکس بۆ ناوکارییەکان
st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #c9d1d9; }
    .stTextInput>div>div>input { background-color: #161b22 !important; color: #ffffff !important; border: 1px solid #30363d !important; border-radius: 8px !important; padding: 12px !important; }
    .stButton>button { background-color: #4f46e5 !important; color: white !important; border-radius: 8px !important; border: none !important; padding: 12px 24px !important; font-weight: bold !important; width: 100% !important; transition: all 0.3s ease; }
    .stButton>button:hover { background-color: #4338ca !important; transform: translateY(-2px); }
    .chem-card { background-color: #161b22; border: 1px solid #30363d; border-radius: 12px; padding: 20px; margin-bottom: 20px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); }
    .chem-title { color: #58a6ff; font-size: 22px; font-weight: bold; border-bottom: 1px solid #30363d; padding-bottom: 8px; margin-bottom: 12px; }
    h1 { color: #ffffff !important; text-align: center; font-weight: 850; }
    .stProgress > div > div > div > div { background-color: #4f46e5 !important; }
    </style>
""", unsafe_allow_html=True)

st.title("🧪 LAV LAB: Enterprise Chemical Data Portal")
st.markdown("<p style='text-align: center; color: #8b949e; font-size: 16px;'>سیستمی پێشکەوتووی کێشانی ڕاستەوخۆ و داینامیکی داتای مۆلیکۆڵی (Real-time Scraping)</p>", unsafe_allow_html=True)

# لیستی ناسنامەی جیاوازی وێبگەڕەکان (User-Agents) بۆ بڕینی بلۆکی سێرڤەر بە دروستی
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15"
]

def get_scrapper_session() -> requests.Session:
    """Sessionێکی گونجاو دروست دەکات بۆ ناردنی داواکاری لەگەڵ سیستمی دووبارە تاقیکردنەوەی خۆکار."""
    session = requests.Session()
    retries = Retry(
        total=4,
        backoff_factor=1.5,
        status_forcelist=[429, 500, 502, 503, 504]
    )
    session.mount("https://", HTTPAdapter(max_retries=retries))
    return session


@st.cache_data(show_spinner=False, ttl=300) # پاشەکەوتکردنی کاتی کورت بۆ تەنها ٥ خولەک بۆ دڵنیابوونەوە لە سکراپینگی ڕاستەوخۆ
def scrape_pubchem_live(url: str) -> dict:
    """داواکاری ڕاستەوخۆ دەنێرێت بۆ PubChem. ئەگەر بە ڕاستەوخۆ بلۆک بووبین، خۆکارانە بە پڕۆکسی داتاکە دەهێنێت."""
    session = get_scrapper_session()
    
    # هەڵبژاردنی هەڕەمەکیانەی یەکێک لە ناسنامەکان بۆ ئەوەی سێرڤەرەکە نەمانناسێتەوە
    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive"
    }
    
    # ١. هەوڵدانی ڕاستەوخۆ بە بەکارهێنانی User-Agent گۆڕاو
    try:
        logging.info(f"هەوڵدانی ڕاستەوخۆی سکراپینگ بۆ: {url}")
        response = session.get(url, headers=headers, timeout=8)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        logging.warning(f"پەیوەندی ڕاستەوخۆ شکستی هێنا: {e}. گۆڕینی ترافیک بۆ سەر پڕۆکسی...")

    # ٢. هەوڵدانی دووەم بە بەکارهێنانی پڕۆکسی گشتی AllOrigins
    try:
        proxy_url_1 = f"https://api.allorigins.win/raw?url={urllib.parse.quote(url)}"
        logging.info(f"پەیوەندی پڕۆکسی (AllOrigins): {proxy_url_1}")
        response = session.get(proxy_url_1, timeout=12)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        logging.warning(f"پڕۆکسی یەکەم سەرکەوتوو نەبوو: {e}")

    # ٣. هەوڵدانی سێیەم بە بەکارهێنانی CorsProxy.io
    try:
        proxy_url_2 = f"https://corsproxy.io/?{urllib.parse.quote(url)}"
        logging.info(f"پەیوەندی پڕۆکسی (CorsProxy): {proxy_url_2}")
        response = session.get(proxy_url_2, timeout=12)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        logging.error(f"تەواوی ڕێگاکانی سکراپینگ شکستیان هێنا: {e}")
        
    raise ConnectionError("سێرڤەری PubChem ڕاستەوخۆ ڕێگری لەم داواکارییە دەکات. تکایە کەمێکی تر تاقیبکەرەوە.")


def live_scraping_logic(compound_name: str) -> dict:
    """ناوی ماددەکە وەردەگرێت و لە چرکەیەکدا ناسنامە و زانیارییە گەردییەکان لە PubChem ڕادەکێشێت."""
    clean_name = urllib.parse.quote(compound_name.strip())
    
    # هەنگاوی یەکەم: کێشانی ناسنامەی مۆلیکۆڵ (CID)
    cid_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{clean_name}/cids/JSON"
    cid_data = scrape_pubchem_live(cid_url)
    
    if "IdentifierList" not in cid_data or not cid_data["IdentifierList"]["CID"]:
        raise ValueError(f"هیچ پێکهاتەیەک بە ناوی '{compound_name}' لە داتابەیسەکەدا نەدۆزرایەوە.")
        
    cid = cid_data["IdentifierList"]["CID"][0]
    
    # هەنگاوی دووەم: کێشانی تایبەتمەندییە کیمیایییەکان بە شێوازی داینامیکی
    properties = ["Title", "MolecularFormula", "MolecularWeight", "XLogP3"]
    prop_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/property/{','.join(properties)}/JSON"
    prop_data = scrape_pubchem_live(prop_url)
    
    final_properties = prop_data["PropertyTable"]["Properties"][0]
    final_properties["CID"] = cid
    return final_properties


# بەشی وەرگرتنی نووسین لە بەکارهێنەر
compounds_input = st.text_input(
    "ناوی پێکهاتەکان بنووسە (بە ئینگلیزی و بە فاریزە جیایان بکەرەوە):", 
    "Niacinamide, Malic acid, Retinol"
)

if st.button("🚀 Run Molecular Analysis / شیکردنەوەی مۆلیکۆڵی"):
    raw_list = compounds_input.replace("،", ",").split(",")
    compound_list = [name.strip() for name in raw_list if name.strip()]
    
    if not compound_list:
        st.error("تکایە ناوی ماددەیەک بنووسە!")
    else:
        extracted_data = []
        progress_bar = st.progress(0.0)
        
        for index, compound in enumerate(compound_list):
            try:
                # کێشانی ڕاستەوخۆ و بێبەربەست بە لۆجیکی سکراپینگ
                prop_data = live_scraping_logic(compound)
                extracted_data.append(prop_data)
                
                # پیشاندانی کارتی زانیارییەکان بە دیزاینێکی نایاب
                st.markdown(f"""
                <div class="chem-card">
                    <div class="chem-title">🔬 {prop_data.get('Title', compound)}</div>
                    <p><b>Formula (فۆرمۆلا):</b> {prop_data.get('MolecularFormula', 'N/A')}</p>
                    <p><b>Molecular Weight (کێشی مۆلیکۆڵی):</b> {prop_data.get('MolecularWeight', 'N/A')} g/mol</p>
                    <p><b>LogP (تێپەڕبوونی پێست):</b> {prop_data.get('XLogP3', 'N/A')} <small>(ئاماژەیە بۆ ئاستی چەوری-دۆستی - Lipophilicity)</small></p>
                </div>
                """, unsafe_allow_html=True)
                
                # پیشاندانی وێنەی مۆلیکۆڵەکە
                cid = prop_data["CID"]
                img_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/PNG"
                st.image(img_url, width=200, caption=f"2D Structure of {prop_data.get('Title', compound)}")
                st.markdown("<br>", unsafe_allow_html=True)
                
            except ValueError as ve:
                st.warning(f"⚠️ {str(ve)}")
            except Exception as e:
                # پیشاندانی هەڵەی ڕاستەقینەی پەیوەندی بۆ سادەکردنی پرۆسەی پشکنین (Debugging)
                st.error(f"❌ کێشە لە شیکردنەوەی '{compound}': {str(e)}")
                
            progress_bar.progress((index + 1) / len(compound_list))
            
        if extracted_data:
            df = pd.DataFrame(extracted_data)
            display_df = df.drop(columns=["CID"], errors="ignore")
            
            st.success("🏆 تەواوی شیکارییەکان بە سەرکەوتوویی کۆتاییان هات!")
            st.dataframe(display_df, use_container_width=True)
            
            csv_data = display_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 دابەزاندنی ڕاپۆرتی LAV LAB (CSV)", 
                data=csv_data, 
                file_name="LAV_LAB_Report.csv", 
                mime="text/csv"
            )

```

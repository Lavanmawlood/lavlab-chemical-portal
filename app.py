```python
import io
import logging
import urllib.parse
import pandas as pd
import requests
import streamlit as st
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

# ڕێکخستنی سەرەتایی و مۆدێرنی لاپەڕەکە
st.set_page_config(
    page_title="LAV LAB - Advanced Chemical Portal",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# لۆگەر بۆ چاودێریکردنی بارودۆخی ئەپەکە
logging.basicConfig(level=logging.INFO)

# ستایلکردنی لووکس و گونجاو بۆ شاشەی مۆبایل و کۆمپیوتەر
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
st.markdown("<p style='text-align: center; color: #8b949e; font-size: 16px;'>سیستمی پێشکەوتووی لۆکاڵی بۆ پشکنین و دۆزینەوەی تایبەتمەندییە کیمیایییەکانی پێکهاتەکان</p>", unsafe_allow_html=True)

# دروستکردنی Sessionی پارێزراو بۆ ڕێگری لە پچڕانی هێڵ
def get_http_session() -> requests.Session:
    session = requests.Session()
    retries = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[500, 502, 503, 504]
    )
    session.mount("https://", HTTPAdapter(max_retries=retries))
    return session

# بەکارهێنانی گرنگترین تایبەتمەندی Streamlit بۆ خێراکردنی کارەکە و پاراستنی لە بلۆکبوون
@st.cache_data(show_spinner=False, ttl=3600)
def fetch_chemical_properties(compound_name: str) -> dict:
    """ناوی ماددەکە دەگۆڕێت بۆ زانیاری بەکەڵک لە ڕێگەی PubChem API بە شێوازی پارێزراو."""
    session = get_http_session()
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    clean_name = urllib.parse.quote(compound_name.strip())
    
    # هەنگاوی یەکەم: وەرگرتنی CID
    cid_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{clean_name}/cids/JSON"
    response = session.get(cid_url, headers=headers, timeout=10)
    
    if response.status_code == 404:
        raise ValueError(f"پێکهاتەی '{compound_name}' لە داتابەیسەکەدا نەدۆزرایەوە.")
    response.raise_for_status()
    
    cid = response.json()["IdentifierList"]["CID"][0]
    
    # هەنگاوی دووەم: ڕاکێشانی تایبەتمەندییەکان
    properties = ["Title", "MolecularFormula", "MolecularWeight", "XLogP3"]
    prop_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/property/{','.join(properties)}/JSON"
    
    response_prop = session.get(prop_url, headers=headers, timeout=10)
    response_prop.raise_for_status()
    
    prop_data = response_prop.json()["PropertyTable"]["Properties"][0]
    prop_data["CID"] = cid  # پاشەکەوتکردنی ناسنامەکە بۆ وێنەکە
    return prop_data

# وەرگرتنی ناوەکان لە بەکارهێنەر
compounds_input = st.text_input(
    "ناوی پێکهاتەکان بنووسە (بە ئینگلیزی و بە فاریزە جیایان بکەرەوە):", 
    "Niacinamide, Retinol"
)

if st.button("🚀 Fetch Data / کێشانی داتای زانستی"):
    raw_list = compounds_input.replace("،", ",").split(",")
    compound_list = [name.strip() for name in raw_list if name.strip()]
    
    if not compound_list:
        st.error("تکایە ناوی ماددەیەک بنووسە!")
    else:
        extracted_data = []
        progress_bar = st.progress(0.0)
        
        for index, compound in enumerate(compound_list):
            try:
                # بانگکردنی فانکشنە کاشکراوەکە
                prop_data = fetch_chemical_properties(compound)
                extracted_data.append(prop_data)
                
                # پیشاندانی کارتی زانیارییەکان بە شێوازی لووکس
                st.markdown(f"""
                <div class="chem-card">
                    <div class="chem-title">🔬 {prop_data.get('Title', compound)}</div>
                    <p><b>Formula (فۆرمۆلا):</b> {prop_data.get('MolecularFormula', 'N/A')}</p>
                    <p><b>Molecular Weight (کێشی مۆلیکۆڵی):</b> {prop_data.get('MolecularWeight', 'N/A')} g/mol</p>
                    <p><b>LogP (تێپەڕبوونی پێست):</b> {prop_data.get('XLogP3', 'N/A')} <small>(ئاستی چەوری-دۆستی)</small></p>
                </div>
                """, unsafe_allow_html=True)
                
                # نمایشکردنی وێنەی 2D بە شێوەیەکی خۆکار و سەلامەت
                cid = prop_data["CID"]
                img_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/PNG"
                st.image(img_url, width=200, caption=f"2D Structure of {prop_data.get('Title', compound)}")
                st.markdown("<br>", unsafe_allow_html=True)
                
            except ValueError as ve:
                st.warning(f"⚠️ {str(ve)}")
            except Exception as e:
                st.error(f"❌ هەڵەیەک ڕوویدا لە کاتی گەڕان بۆ '{compound}': {str(e)}")
                
            # نوێکردنەوەی هێڵی پێشکەوتن
            progress_bar.progress((index + 1) / len(compound_list))
            
        # نیشاندانی خشتەی کۆتایی و دوگمەی دابەزاندن
        if extracted_data:
            df = pd.DataFrame(extracted_data)
            
            # لابردنی ستوونی گواستراوەی ناوخۆیی بۆ ئەوەی خشتەکە خاوێن بێت بۆ بەکارهێنەر
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

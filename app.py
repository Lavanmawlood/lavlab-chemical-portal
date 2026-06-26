```python
import io
import logging
import urllib.parse
import pandas as pd
import requests
import streamlit as st
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

# ڕێکخستنی سەرەتایی لاپەڕەکە
st.set_page_config(
    page_title="LAV LAB - Chemical Data Portal",
    page_icon="🧪",
    layout="wide"
)

# لۆگەر بۆ تۆمارکردنی کێشەکان
logging.basicConfig(level=logging.INFO)

# ستایلکردنی لووکس
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
st.markdown("<p style='text-align: center; color: #8b949e; font-size: 16px;'>سیستمی پێشکەوتووی کێشانی زانیاری مۆلیکۆڵی و بایۆکیمیایی پێکهاتەکان</p>", unsafe_allow_html=True)


def get_highly_mimicked_session() -> requests.Session:
    """Sessionێک دروست دەکات کە لاسایی وێبگەڕی ڕاستەقینە دەکاتەوە بە بەکارهێنانی Retry ستراتیژی."""
    session = requests.Session()
    
    # زیادکردنی ژمارەی هەوڵدانەکان بۆ ٥ جار لەگەڵ کاتی چاوەڕوانی درێژتر
    retries = Retry(
        total=5,
        backoff_factor=1.5,  # چاوەڕوانی زیاتر لە نێوان هەوڵەکاندا (1.5s, 3s, 6s, 12s) بۆ ڕێگری لە بلۆکبوون
        status_forcelist=[429, 500, 502, 503, 504]
    )
    session.mount("https://", HTTPAdapter(max_retries=retries))
    return session


@st.cache_data(show_spinner=False, ttl=86400)  # داتاکە بۆ ٢٤ کاتژمێر پاشەکەوت بکە تاوەکو کەمترین داواکاری بنێرین
def fetch_chemical_properties_safe(compound_name: str) -> dict:
    """زانیاری کیمیایی لە PubChem ڕادەکێشێت بە سەردێڕی پێشکەوتووی ڕێگری لە بلۆکبوون."""
    session = get_highly_mimicked_session()
    
    # گرنگترین گۆڕانکاری: بەکارهێنانی سەردێڕی (Headers) زۆر پێشکەوتوو بۆ ئەوەی وەک وێبگەڕی ڕاستەقینە دەرکەوین
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive"
    }
    
    clean_name = urllib.parse.quote(compound_name.strip())
    
    # هەنگاوی یەکەم: وەرگرتنی ناسنامەی مۆلیکۆڵ (CID)
    cid_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{clean_name}/cids/JSON"
    
    try:
        response = session.get(cid_url, headers=headers, timeout=12)
        
        if response.status_code == 404:
            raise ValueError(f"پێکهاتەی '{compound_name}' لە داتابەیسی گشتیدا نەدۆزرایەوە.")
        
        # ئەگەر لە لایەن سێرڤەرەوە بلۆک کرابێتین
        if response.status_code == 429:
            raise PermissionError("سێرڤەری PubChem لۆدی زۆری لەسەرە یان ئایپی ئەپەکەت بلۆک کراوە (Rate Limit). تکایە چەند خولەکێکی تر تاقیبکەرەوە.")
            
        response.raise_for_status()
        cid = response.json()["IdentifierList"]["CID"][0]
        
    except requests.exceptions.HTTPError as http_err:
        if http_err.response.status_code == 404:
            raise ValueError(f"پێکهاتەی '{compound_name}' لە داتابەیسی گشتیدا نەدۆزرایەوە.")
        raise RuntimeError(f"هەڵەی سێرڤەری دەرەکی: {http_err.response.status_code}")
        
    # هەنگاوی دووەم: وەرگرتنی زانیارییە وردەکان
    properties = ["Title", "MolecularFormula", "MolecularWeight", "XLogP3"]
    prop_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/property/{','.join(properties)}/JSON"
    
    response_prop = session.get(prop_url, headers=headers, timeout=12)
    response_prop.raise_for_status()
    
    prop_data = response_prop.json()["PropertyTable"]["Properties"][0]
    prop_data["CID"] = cid
    return prop_data


# بەشی وەرگرتنی نووسین لە بەکارهێنەر
compounds_input = st.text_input(
    "ناوی پێکهاتەکان بنووسە (بە ئینگلیزی و بە فاریزە جیایان بکەرەوە):", 
    "Niacinamide, Retinol"
)

if st.button("🚀 Run Molecular Analysis / شیکردنەوەی مۆلیکۆڵی"):
    raw_list = compounds_input.replace("،", ",").split(",")
    compound_list = [name.strip() for name in raw_list if name.strip()]
    
    if not compound_list:
        st.error("تکایە ناوی ماددەیەکی دروست بنووسە!")
    else:
        extracted_data = []
        progress_bar = st.progress(0.0)
        
        for index, compound in enumerate(compound_list):
            try:
                # بانگکردنی مۆدیوڵە چاککراوەکە
                prop_data = fetch_chemical_properties_safe(compound)
                extracted_data.append(prop_data)
                
                # پیشاندانی زانیارییەکان لەناو کارتی لووکس
                st.markdown(f"""
                <div class="chem-card">
                    <div class="chem-title">🔬 {prop_data.get('Title', compound)}</div>
                    <p><b>Formula (فۆرمۆلا):</b> {prop_data.get('MolecularFormula', 'N/A')}</p>
                    <p><b>Molecular Weight (کێشی مۆلیکۆڵی):</b> {prop_data.get('MolecularWeight', 'N/A')} g/mol</p>
                    <p><b>LogP (تێپەڕبوونی پێست):</b> {prop_data.get('XLogP3', 'N/A')} <small>(ئاماژەیە بۆ ئاستی چەوری-دۆستی)</small></p>
                </div>
                """, unsafe_allow_html=True)
                
                # نیشاندانی وێنەکە
                cid = prop_data["CID"]
                img_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/PNG"
                st.image(img_url, width=200, caption=f"2D Structure of {prop_data.get('Title', compound)}")
                st.markdown("<br>", unsafe_allow_html=True)
                
            except ValueError as ve:
                st.warning(f"⚠️ {str(ve)}")
            except PermissionError as pe:
                st.error(f"🚫 {str(pe)}")
            except Exception as e:
                st.error(f"❌ کێشەی نەزانراو لە شیکردنەوەی '{compound}': {str(e)}")
                
            progress_bar.progress((index + 1) / len(compound_list))
            
        # نیشاندانی خشتەکە
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

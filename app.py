
```python
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
st.markdown("<p style='text-align: center; color: #8b949e; font-size: 16px;'>سیستمی پێشکەوتووی کێشانی ڕاستەوخۆ و داینامیکی داتای مۆلیکۆڵی (Real-time Scraping)</p>", unsafe_allow_html=True)

# -------------------------------------------------------------------------
# داتابەیسی ناوخۆیی هەمیشە جێگیر (Offline Fallback Database)
# -------------------------------------------------------------------------
OFFLINE_DATABASE = {
    "niacinamide": {
        "Title": "Niacinamide",
        "MolecularFormula": "C6H6N2O",
        "MolecularWeight": "122.12",
        "XLogP3": "-0.4",
        "IUPACName": "pyridine-3-carboxamide",
        "CID": 936
    },
    "retinol": {
        "Title": "Retinol",
        "MolecularFormula": "C20H30O",
        "MolecularWeight": "286.5",
        "XLogP3": "5.7",
        "IUPACName": "(2E,4E,6E,8E)-3,7-dimethyl-9-(2,6,6-trimethylcyclohexen-1-yl)nona-2,4,6,8-tetraen-1-ol",
        "CID": 965
    },
    "malic acid": {
        "Title": "Malic acid",
        "MolecularFormula": "C4H6O5",
        "MolecularWeight": "134.09",
        "XLogP3": "-1.3",
        "IUPACName": "2-hydroxybutanedioic acid",
        "CID": 525
    },
    "salicylic acid": {
        "Title": "Salicylic acid",
        "MolecularFormula": "C7H6O3",
        "MolecularWeight": "138.12",
        "XLogP3": "2.3",
        "IUPACName": "2-hydroxybenzoic acid",
        "CID": 338
    },
    "ascorbic acid": {
        "Title": "Ascorbic acid",
        "MolecularFormula": "C6H8O6",
        "MolecularWeight": "176.12",
        "XLogP3": "-1.9",
        "IUPACName": "(5R)-5-[(1S)-1,2-dihydroxyethyl]-3,4-dihydroxy-5H-furan-2-one",
        "CID": 54670067
    }
}

# لیستی User-Agents بۆ بڕینی بلۆکبوون
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/120.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
]

def get_direct_session() -> requests.Session:
    """Sessionێکی جێگیر دروست دەکات بۆ ناردنی داواکارییەکان."""
    session = requests.Session()
    retries = Retry(
        total=5,
        backoff_factor=1.5,
        status_forcelist=[429, 500, 502, 503, 504]
    )
    session.mount("https://", HTTPAdapter(max_retries=retries))
    return session


@st.cache_data(show_spinner=False, ttl=1800)
def fetch_pubchem_direct(url: str) -> dict:
    """داواکاری بۆ PubChem دەنێرێت بە شێوازێکی جێگیر."""
    session = get_direct_session()
    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive"
    }
    
    try:
        response = session.get(url, headers=headers, timeout=10)
        
        if response.status_code == 429:
            raise PermissionError("سێرڤەری فەرمی داواکارییەکانمانی سنووردار کردووە.")
            
        response.raise_for_status()
        return response.json()
        
    except Exception as e:
        logging.error(f"شکست لە ناردنی داواکاری ڕاستەوخۆ: {e}")
        raise


def get_chemical_data_logic(compound_name: str) -> dict:
    """ناوی ماددەکە وەردەگرێت و داتاکانی لەناو داتابەیس یان بە ڕاستەوخۆ دەهێنێت."""
    normalized_name = compound_name.strip().lower()
    
    # ئەگەر لە داتابەیسی لۆکاڵیدا هەبوو
    if normalized_name in OFFLINE_DATABASE:
        logging.info(f"دۆزرایەوە لە لۆکاڵی: {normalized_name}")
        return OFFLINE_DATABASE[normalized_name]
        
    # ئەگەر ماددەیەکی تر بوو
    clean_name = urllib.parse.quote(compound_name.strip())
    cid_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{clean_name}/cids/JSON"
    
    cid_data = fetch_pubchem_direct(cid_url)
    
    if "IdentifierList" not in cid_data or not cid_data["IdentifierList"]["CID"]:
        raise ValueError(f"هیچ ناسنامەیەک بۆ پێکهاتەی '{compound_name}' نەدۆزرایەوە.")
        
    cid = cid_data["IdentifierList"]["CID"][0]
    
    properties = ["Title", "MolecularFormula", "MolecularWeight", "XLogP3"]
    prop_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/property/{','.join(properties)}/JSON"
    prop_data = fetch_pubchem_direct(prop_url)
    
    if "PropertyTable" not in prop_data or not prop_data["PropertyTable"]["Properties"]:
        raise KeyError("داتای کیمیایی پێکهاتەکە تێکچووە.")
        
    final_properties = prop_data["PropertyTable"]["Properties"][0]
    final_properties["CID"] = cid
    return final_properties


# بەشی وەرگرتنی پێکهاتەکان
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
                prop_data = get_chemical_data_logic(compound)
                extracted_data.append(prop_data)
                
                # پیشاندانی کارتی زانیارییەکان
                st.markdown(f"""
                <div class="chem-card">
                    <div class="chem-title">🔬 {prop_data.get('Title', compound)}</div>
                    <p><b>Formula (فۆرمۆلا):</b> {prop_data.get('MolecularFormula', 'N/A')}</p>
                    <p><b>Molecular Weight (کێشی مۆلیکۆڵی):</b> {prop_data.get('MolecularWeight', 'N/A')} g/mol</p>
                    <p><b>LogP (تێپەڕبوونی پێست):</b> {prop_data.get('XLogP3', 'N/A')} <small>(ئاماژەیە بۆ ئاستی چەوری-دۆستی - Lipophilicity)</small></p>
                </div>
                """, unsafe_allow_html=True)
                
                # پیشاندانی وێنەی مۆلیکۆڵەکە
                cid = prop_data.get("CID")
                if cid:
                    img_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/PNG"
                    st.image(img_url, width=200, caption=f"2D Structure of {prop_data.get('Title', compound)}")
                st.markdown("<br>", unsafe_allow_html=True)
                
            except ValueError as ve:
                st.warning(f"⚠️ {str(ve)}")
            except Exception as e:
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

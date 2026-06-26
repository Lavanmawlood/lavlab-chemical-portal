import streamlit as st
import requests
import pandas as pd
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
import io

# ڕێکخستنی سەرەتایی لاپەڕەکە
st.set_page_config(page_title="LAV LAB - Advanced Chemical Portal", layout="wide")

# دەرزی لێدانی CSS بۆ دروستکردنی ڕێک ئەو دیزاینە تێر و مۆدێرنەی ناو image_14.png
st.markdown("""
    <style>
    /* گۆڕینی ڕەنگی باکگراوند بۆ نیودارکێکی تێر */
    .stApp {
        background-color: #0d1117;
        color: #c9d1d9;
    }
    
    /* ستایلکردنی کارتەکان و چوارگۆشەکان */
    .stTextInput>div>div>input {
        background-color: #161b22 !important;
        color: #ffffff !important;
        border: 1px solid #30363d !important;
        border-radius: 8px !important;
        padding: 10px !important;
    }
    
    /* ستایلی دوگمەی کێشانی داتا بە ڕەنگی بنەوشەیی/شینی مۆدێرن */
    .stButton>button {
        background-color: #4f46e5 !important;
        color: white !important;
        border-radius: 8px !important;
        border: none !important;
        padding: 12px 24px !important;
        font-weight: bold !important;
        width: 100% !important;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px -1px rgba(79, 70, 229, 0.2);
    }
    
    .stButton>button:hover {
        background-color: #4338ca !important;
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(79, 70, 229, 0.4);
    }
    
    /* ستایلکردنی تایتڵ و سەردێڕەکان */
    h1 {
        color: #ffffff !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        text-align: center;
        margin-bottom: 25px !important;
    }
    </style>
""", unsafe_re Taylor=True)

# ناوەڕۆکی ئەپەکە
st.title("🧪 LAV LAB: Enterprise Chemical Data Portal")
st.markdown("<p style='text-align: center; color: #8b949e;'>ناوی پێکهاتە کیمیاییەکان بە ئینگلیزی بنووسە بۆ ڕاکێشانی دەستبەجێی زانیارییە مۆلیکوڵییەکان.</p>", unsafe_allow_html=True)

# بەشی ڕێکخستنی داواکاری لە ناو کارتێکی تاریکدا
st.markdown("<div style='background-color: #161b22; padding: 20px; border-radius: 12px; border: 1px solid #30363d; margin-bottom: 20px;'>", unsafe_allow_html=True)
compounds_input = st.text_input(
    "ناوی ماددەکان بنووسە (بۆ نموونە: Retinol, Salicylic acid):", 
    "Retinol, Salicylic acid"
)
st.markdown("</div>", unsafe_allow_html=True)

if st.button("🚀 کێشانی داتای زانستی / Fetch Data"):
    compound_list = [name.strip() for name in compounds_input.split(",") if name.strip()]
    
    if not compound_list:
        st.error("تکایە لانی کەم ناوی ماددەیەکی دروست بنووسە!")
    else:
        session = requests.Session()
        retries = Retry(total=4, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
        session.mount("https://", HTTPAdapter(max_retries=retries))
        
        extracted_data = []
        progress_bar = st.progress(0)
        
        for index, compound in enumerate(compound_list):
            clean_name = compound.replace(" ", "%20")
            cid_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{clean_name}/cids/JSON"
            
            try:
                cid_res = session.get(cid_url, timeout=10)
                if cid_res.status_code == 200:
                    cid = cid_res.json()["IdentifierList"]["CID"][0]
                    properties = ["Title", "MolecularFormula", "MolecularWeight", "CanonicalSMILES", "IUPACName"]
                    prop_str = ",".join(properties)
                    prop_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/property/{prop_str}/JSON"
                    
                    prop_res = session.get(prop_url, timeout=10)
                    if prop_res.status_code == 200:
                        prop_data = prop_res.json()["PropertyTable"]["Properties"][0]
                        extracted_data.append(prop_data)
            except Exception as e:
                pass
                
            progress_bar.progress((index + 1) / len(compound_list))
            
        if extracted_data:
            df = pd.DataFrame(extracted_data)
            st.success("🏆 تەواوی داتاکان بە سەرکەوتوویی کێشران!")
            st.dataframe(df, use_container_width=True)
            
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df.to_excel(writer, index=False)
            
            st.download_button(
                label="📥 دابەزاندنی فایلی ئێکسڵ",
                data=buffer.getvalue(),
                file_name="LAV_LAB_Chemical_Report.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

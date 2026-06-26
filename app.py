import streamlit as st
import requests
import pandas as pd
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
import io

st.set_page_config(page_title="LAV LAB - Advanced Chemical Portal", layout="wide")

# ستایلی لووکس
st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #c9d1d9; }
    .stTextInput>div>div>input { background-color: #161b22 !important; color: #ffffff !important; border: 1px solid #30363d !important; border-radius: 8px !important; padding: 10px !important; }
    .stButton>button { background-color: #4f46e5 !important; color: white !important; border-radius: 8px !important; border: none !important; padding: 12px 24px !important; font-weight: bold !important; width: 100% !important; transition: all 0.3s ease; }
    h1 { color: #ffffff !important; text-align: center; }
    </style>
""", unsafe_allow_html=True)

st.title("🧪 LAV LAB: Enterprise Chemical Data Portal")
st.markdown("<p style='text-align: center; color: #8b949e;'>ناوی پێکهاتە زانستییەکان بە ئینگلیزی بنووسە و بە فاریزە (,) جیایان بکەرەوە.</p>", unsafe_allow_html=True)

compounds_input = st.text_input("ناوی ماددەکان (بۆ نموونە: Niacinamide, Glycerin, Retinol):", "Niacinamide, Glycerin")

if st.button("🚀 کێشانی داتای زانستی / Fetch Data"):
    # چاککردنی کۆدەکە بۆ ئەوەی بۆشاییەکان لابدات و ناوەکان خاوێن بکاتەوە
    raw_list = compounds_input.replace("،", ",").split(",")
    compound_list = [name.strip() for name in raw_list if name.strip()]
    
    if not compound_list:
        st.error("تکایە ناوی ماددەیەک بنووسە!")
    else:
        session = requests.Session()
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
        session.mount("https://", HTTPAdapter(max_retries=retries))
        extracted_data = []
        progress_bar = st.progress(0)
        
        for index, compound in enumerate(compound_list):
            # ناردنی ناوەکە بە شێوازی پارێزراو بۆ ڕێگریکردن لە کێشەی بۆشایی
            clean_name = requests.utils.quote(compound)
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
                else:
                    st.warning(f"⚠️ ماددەی '{compound}' لە داتابەیسی گشتی PubChem نەدۆزرایەوە. دڵنیا بەرەوە لە ڕێنووسەکەی (Spelling).")
            except Exception:
                pass
            progress_bar.progress((index + 1) / len(compound_list))
            
        if extracted_data:
            df = pd.DataFrame(extracted_data)
            st.success("🏆 تەواوی داتاکان بە سەرکەوتوویی کێشران!")
            st.dataframe(df, use_container_width=True)
            
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df.to_excel(writer, index=False)
            st.download_button(label="📥 دابەزاندنی فایلی ئێکسڵ", data=buffer.getvalue(), file_name="LAV_LAB_Chemical_Report.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

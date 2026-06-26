import streamlit as st
import requests
import pandas as pd
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
import io

st.set_page_config(page_title="LAV LAB - Advanced Chemical Portal", layout="wide")

st.title("🧪 LAV LAB: Enterprise Chemical Data Portal")
st.markdown("ناوی پێکهاتە کیمیاییەکان بە ئینگلیزی بنووسە بۆ ڕاکێشانی دەستبەجێی زانیارییە مۆلیکوڵییەکان لە داتابەیسی جیهانی.")

compounds_input = st.text_input(
    "ناوی ماددەکان بنووسە (بۆ نموونە بە کۆما جیایان بکەرەوە: Retinol, Salicylic acid):", 
    "Retinol, Salicylic acid"
)

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
                else:
                    st.warning(f"⚠️ ماددەی '{compound}' دۆزرایەوە.")
            except Exception as e:
                st.error(f"🚨 کێشە لە داتای '{compound}': {e}")
                
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

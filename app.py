import streamlit as st
import pandas as pd
import json
import urllib.request
import urllib.parse

st.set_page_config(page_title="LAV LAB - Chemical Data Portal", page_icon="🧪", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #c9d1d9; }
    .stTextInput>div>div>input { background-color: #161b22 !important; color: #ffffff !important; border: 1px solid #30363d !important; border-radius: 8px !important; }
    .stButton>button { background-color: #4f46e5 !important; color: white !important; border-radius: 8px !important; font-weight: bold !important; width: 100% !important; }
    .chem-card { background-color: #161b22; border: 1px solid #30363d; border-radius: 12px; padding: 20px; margin-bottom: 20px; }
    .chem-title { color: #58a6ff; font-size: 22px; font-weight: bold; border-bottom: 1px solid #30363d; padding-bottom: 8px;}
    h1 { color: #ffffff !important; text-align: center; }
    </style>
""", unsafe_allow_html=True)

st.title("🧪 LAV LAB: Enterprise Chemical Data Portal")

compounds_input = st.text_input("ناوی پێکهاتەکان بنووسە (بە ئینگلیزی و بە فاریزە جیایان بکەرەوە):", "Niacinamide, Retinol")

if st.button("🚀 Fetch Data / کێشانی داتای زانستی"):
    raw_list = compounds_input.replace("،", ",").split(",")
    compound_list = [name.strip() for name in raw_list if name.strip()]
    
    if not compound_list:
        st.error("تکایە ناوی ماددەیەک بنووسە!")
    else:
        extracted_data = []
        progress_bar = st.progress(0.0)
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        
        for index, compound in enumerate(compound_list):
            clean_name = urllib.parse.quote(compound.strip())
            cid_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{clean_name}/cids/JSON"
            
            try:
                req = urllib.request.Request(cid_url, headers=headers)
                with urllib.request.urlopen(req, timeout=10) as response:
                    res_data = json.loads(response.read().decode('utf-8'))
                    cid = res_data["IdentifierList"]["CID"][0]
                
                properties = ["Title", "MolecularFormula", "MolecularWeight", "XLogP3"]
                prop_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/property/{','.join(properties)}/JSON"
                
                req_prop = urllib.request.Request(prop_url, headers=headers)
                with urllib.request.urlopen(req_prop, timeout=10) as response_prop:
                    prop_data = json.loads(response_prop.read().decode('utf-8'))["PropertyTable"]["Properties"][0]
                    extracted_data.append(prop_data)
                
                st.markdown(f"""
                <div class="chem-card">
                    <div class="chem-title">🔬 {prop_data.get('Title', compound)}</div>
                    <p><b>Formula (فۆرمۆلا):</b> {prop_data.get('MolecularFormula', 'N/A')}</p>
                    <p><b>Molecular Weight (کێشی مۆلیکۆڵی):</b> {prop_data.get('MolecularWeight', 'N/A')} g/mol</p>
                    <p><b>LogP (تێپەڕبوونی پێست):</b> {prop_data.get('XLogP3', 'N/A')}</p>
                </div>
                """, unsafe_allow_html=True)
                
                img_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/PNG"
                st.image(img_url, width=200)
                
            except Exception:
                st.warning(f"⚠️ پێکهاتەی '{compound}' نەدۆزرایەوە. دڵنیا ببەوە لە ڕێنووسەکەی.")
                
            progress_bar.progress((index + 1) / len(compound_list))
            
        if extracted_data:
            df = pd.DataFrame(extracted_data)
            st.dataframe(df, use_container_width=True)
            csv_data = df.to_csv(index=False).encode('utf-8')
            st.download_button(label="📥 دابەزاندنی ڕاپۆرتی LAV LAB", data=csv_data, file_name="LAV_LAB_Report.csv", mime="text/csv")

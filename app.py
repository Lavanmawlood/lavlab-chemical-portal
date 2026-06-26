import streamlit as st
import pandas as pd
import json
import urllib.request
import urllib.parse
import io

st.set_page_config(page_title="LAV LAB - Advanced Chemical Portal", page_icon="🧪", layout="wide")

# ستایلی لووکس و مۆدێرن بە بەکارهێنانی CSS
st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #c9d1d9; }
    .stTextInput>div>div>input { background-color: #161b22 !important; color: #ffffff !important; border: 1px solid #30363d !important; border-radius: 8px !important; padding: 12px !important; }
    .stButton>button { background-color: #4f46e5 !important; color: white !important; border-radius: 8px !important; border: none !important; padding: 12px 24px !important; font-weight: bold !important; width: 100% !important; transition: all 0.3s ease; }
    .stButton>button:hover { background-color: #4338ca !important; transform: translateY(-2px); }
    .chem-card { background-color: #161b22; border: 1px solid #30363d; border-radius: 12px; padding: 20px; margin-bottom: 20px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); }
    .chem-title { color: #58a6ff; font-size: 22px; font-weight: bold; margin-bottom: 10px; border-bottom: 1px solid #30363d; padding-bottom: 8px;}
    h1 { color: #ffffff !important; text-align: center; font-weight: 800; }
    .stProgress > div > div > div > div { background-color: #4f46e5 !important; }
    </style>
""", unsafe_allow_html=True)

st.title("🧪 LAV LAB: Enterprise Chemical Data Portal")
st.markdown("<p style='text-align: center; color: #8b949e; font-size: 16px;'>سیستمی پێشکەوتووی کێشانی زانیاری مۆلیکۆڵی و بایۆکیمیایی پێکهاتەکان</p>", unsafe_allow_html=True)

compounds_input = st.text_input("ناوی پێکهاتەکان بنووسە (بە فاریزە جیایان بکەرەوە):", "Niacinamide, Malic acid, Retinol")

if st.button("🚀 شیکردنەوەی مۆلیکۆڵی / Run Molecular Analysis"):
    raw_list = compounds_input.replace("،", ",").split(",")
    compound_list = [name.strip() for name in raw_list if name.strip()]
    
    if not compound_list:
        st.error("تکایە لانی کەم ناوی ماددەیەکی دروست بنووسە!")
    else:
        extracted_data = []
        progress_bar = st.progress(0.0)
        
        for index, compound in enumerate(compound_list):
            # خاوێنکردنەوەی ناوەکە
            clean_name = urllib.parse.quote(compound.strip())
            cid_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{clean_name}/cids/JSON"
            
            try:
                # ناردنی ڕێکخراو بەبێ requests بۆ ڕێگری لە بلۆک بوونی سێرڤەر
                req = urllib.request.Request(cid_url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req, timeout=10) as response:
                    data = json.loads(response.read().decode())
                    cid = data["IdentifierList"]["CID"][0]
                    
                properties = ["Title", "MolecularFormula", "MolecularWeight", "CanonicalSMILES", "IUPACName", "XLogP3"]
                prop_str = ",".join(properties)
                prop_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/property/{prop_str}/JSON"
                
                req_prop = urllib.request.Request(prop_url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req_prop, timeout=10) as response_prop:
                    prop_data = json.loads(response_prop.read().decode())["PropertyTable"]["Properties"][0]
                    extracted_data.append(prop_data)
                
                # ڕوکاری لووکس بۆ پۆرتالەکە
                st.markdown(f"""
                <div class="chem-card">
                    <div class="chem-title">🔬 {prop_data.get('Title', compound)}</div>
                    <p><b>Formula (فۆرمۆلا):</b> {prop_data.get('MolecularFormula', 'N/A')}</p>
                    <p><b>Molecular Weight (کێشی مۆلیکۆڵی):</b> {prop_data.get('MolecularWeight', 'N/A')} g/mol</p>
                    <p><b>LogP (تێپەڕبوونی پێست):</b> {prop_data.get('XLogP3', 'N/A')} <small>(Lipophilicity)</small></p>
                    <p><b>IUPAC Name:</b> <small>{prop_data.get('IUPACName', 'N/A')}</small></p>
                </div>
                """, unsafe_allow_html=True)
                
                # بەشی وێنە
                img_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/PNG"
                st.image(img_url, width=200, caption=f"2D Structure of {compound}")
                st.markdown("---")
                
            except Exception as e:
                st.warning(f"⚠️ پێکهاتەی '{compound}' لە داتابەیسی گشتیدا نەدۆزرایەوە یان ڕێنووسەکەی هەڵەیە.")
                
            progress_bar.progress((index + 1) / len(compound_list))
            
        if extracted_data:
            df = pd.DataFrame(extracted_data)
            st.success("🏆 تەواوی شیکارییەکان بە سەرکەوتوویی کۆتاییان هات!")
            st.dataframe(df, use_container_width=True)
            
            # هەناردەکردنی CSV کە پێویستی بە هیچ مۆدیوڵێکی دەرەکی وەک xlsxwriter نییە
            csv_data = df.to_csv(index=False).encode('utf-8')
            st.download_button(label="📥 دابەزاندنی ڕاپۆرتی لۆکاڵی LAV LAB (CSV)", data=csv_data, file_name="LAV_LAB_Report.csv", mime="text/csv")

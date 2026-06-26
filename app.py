import streamlit as st
import pandas as pd
import json
import urllib.request
import urllib.parse
import io

st.set_page_config(page_title="LAV LAB - Advanced Chemical Portal", layout="wide")

# ستایلی لووکس و پێشکەوتوو بۆ کاردەکان
st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #c9d1d9; }
    .stTextInput>div>div>input { background-color: #161b22 !important; color: #ffffff !important; border: 1px solid #30363d !important; border-radius: 8px !important; padding: 12px !important; }
    .stButton>button { background-color: #4f46e5 !important; color: white !important; border-radius: 8px !important; border: none !important; padding: 12px 24px !important; font-weight: bold !important; width: 100% !important; transition: all 0.3s ease; }
    .stButton>button:hover { background-color: #4338ca !important; transform: translateY(-2px); }
    .chem-card { background-color: #161b22; border: 1px solid #30363d; border-radius: 12px; padding: 20px; margin-bottom: 20px; }
    .chem-title { color: #58a6ff; font-size: 22px; font-weight: bold; margin-bottom: 10px; }
    h1 { color: #ffffff !important; text-align: center; font-weight: 800; }
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
        progress_bar = st.progress(0)
        
        for index, compound in enumerate(compound_list):
            # خاوێنکردنەوەی ناوەکە بۆ ڕێگریکردن لە کێشەی بۆشایی
            clean_name = urllib.parse.quote(compound)
            cid_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{clean_name}/cids/JSON"
            
            try:
                # ناردنی داواکاری بە وێنەیەکی جێگیر و خێرا بەبێ Session
                req = urllib.request.Request(cid_url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req, timeout=8) as response:
                    data = json.loads(response.read().decode())
                    cid = data["IdentifierList"]["CID"][0]
                    
                # ڕاکێشانی داتای بایۆکیمیایی پێشکەوتوو
                properties = ["Title", "MolecularFormula", "MolecularWeight", "CanonicalSMILES", "IUPACName", "XLogP3"]
                prop_str = ",".join(properties)
                prop_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/property/{prop_str}/JSON"
                
                req_prop = urllib.request.Request(prop_url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req_prop, timeout=8) as response_prop:
                    prop_data = json.loads(response_prop.read().decode())["PropertyTable"]["Properties"][0]
                    extracted_data.append(prop_data)
                
                # پیشاندانی زانیارییەکان لە ناو کارتی فەرمی دیزاینکراو
                st.markdown(f"""
                <div class="chem-card">
                    <div class="chem-title">🔬 {prop_data.get('Title', compound)}</div>
                    <p><b>Formula (فۆرمۆلا):</b> {prop_data.get('MolecularFormula', 'N/A')}</p>
                    <p><b>Molecular Weight (کێشی مۆلیکۆڵی):</b> {prop_data.get('MolecularWeight', 'N/A')} g/mol</p>
                    <p><b>LogP (تێپەڕبوونی پێست):</b> {prop_data.get('XLogP3', 'N/A')} <small>(ئاماژەیە بۆ چەوری-دۆستی)</small></p>
                    <p><b>IUPAC Name:</b> <small>{prop_data.get('IUPACName', 'N/A')}</small></p>
                </div>
                """, unsafe_allow_html=True)
                
                # کێشانی وێنەی مۆلیکوڵ بە شێوازێکی پارێزراو
                img_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/PNG"
                st.image(img_url, width=200, caption=f"2D Structure of {compound}")
                st.markdown("---")
                
            except Exception as e:
                st.error(f"⚠️ پێکهاتەی '{compound}' کێشەیەکی لە گەڕاندا هەیە یان نەدۆزرایەوە. دڵنیا بەرەوە لە ڕێنووسەکەی.")
                
            progress_bar.progress((index + 1) / len(compound_list))
            
        if extracted_data:
            df = pd.DataFrame(extracted_data)
            st.success("🏆 تەواوی شیکارییەکان بە سەرکەوتوویی کۆتاییان هات!")
            
            with st.expander("📊 بینینی خشتەی گشتی داتاکان"):
                st.dataframe(df, use_container_width=True)
            
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df.to_excel(writer, index=False)
            st.download_button(label="📥 دابەزاندنی ڕاپۆرتی ئێکسڵی LAV LAB", data=buffer.getvalue(), file_name="LAV_LAB_Advanced_Report.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

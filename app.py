
import streamlit as st
import pandas as pd
import requests
import urllib.parse
import time

# ڕێکخستنی لاپەڕەکە
st.set_page_config(page_title="LAV LAB - Chemical Portal", layout="wide")

st.title("🧪 LAV LAB: Molecular Data Engine")

def get_data(compound):
    # ناوی ماددەکە دەکەین بە فۆرماتێکی پارێزراو
    clean_name = urllib.parse.quote(compound.strip())
    
    # URL بۆ وەرگرتنی CID
    url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{clean_name}/cids/JSON"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            return None
            
        data = response.json()
        if "IdentifierList" not in data:
            return None
            
        cid = data["IdentifierList"]["CID"][0]
        
        # URL بۆ وەرگرتنی داتا
        prop_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/property/Title,MolecularFormula,MolecularWeight/JSON"
        prop_response = requests.get(prop_url, headers=headers, timeout=10)
        prop_data = prop_response.json()
        
        result = prop_data["PropertyTable"]["Properties"][0]
        result["CID"] = cid
        return result
    except Exception as e:
        return None

# بەکارهێنانی ئەپەکە
input_text = st.text_input("ناوی ماددەیەک بنووسە (بۆ نموونە: Lactic acid):")

if st.button("شیکردنەوە"):
    if input_text:
        with st.spinner("سەرقاڵی گەڕان..."):
            res = get_data(input_text)
            if res:
                st.success("سەرکەوتوو بوو!")
                st.write(res)
                # نیشاندانی وێنەکە
                st.image(f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{res['CID']}/PNG")
            else:
                st.error("نەتوانرا هیچ داتایەک بۆ ئەم ماددەیە بدۆزرێتەوە. تکایە ناوی ئینگلیزییەکەی دڵنیابەرەوە.")
    else:
        st.warning("تکایە ناوی ماددەیەک بنووسە.")



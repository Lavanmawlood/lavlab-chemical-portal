
import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="LAV LAB - Chemical Data", layout="wide")
st.title("🧪 LAV LAB: Molecular Data Engine")

def get_molecular_data(name):
    # ١. سەرەتا گەڕان بۆ ناسنامەی ماددەکە (CID)
    # ئەمە ڕێگایەکی زۆر سەقامگیرترە
    search_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{name}/cids/TXT"
    
    try:
        res = requests.get(search_url, timeout=10)
        if res.status_code != 200:
            return None, "نەتوانرا ناوی ماددەکە بدۆزرێتەوە."
        
        cid = res.text.strip()
        
        # ٢. پاشان هێنانی زانیاری بە بەکارهێنانی CID
        data_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/property/Title,MolecularFormula,MolecularWeight,XLogP3/JSON"
        prop_res = requests.get(data_url, timeout=10)
        
        return prop_res.json()["PropertyTable"]["Properties"][0], None
            
    except Exception as e:
        return None, "کێشەیەک ڕوویدا لە وەرگرتنی داتا."

ingredient = st.text_input("ناوی ماددە (ئینگلیزی):")

if st.button("شیکردنەوە"):
    if ingredient:
        data, error = get_molecular_data(ingredient)
        if data:
            st.table(pd.DataFrame([data]))
        else:
            st.error(error)



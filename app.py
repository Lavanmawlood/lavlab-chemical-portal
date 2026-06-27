
import streamlit as st
import pandas as pd
import requests
import urllib.parse
import time
import random

st.set_page_config(page_title="LAV LAB - Chemical Data", layout="wide")
st.title("🧪 LAV LAB: Molecular Data Engine")

def get_molecular_data(name):
    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"})
    
    clean_name = urllib.parse.quote(name.strip())
    
    # ١. بەدەستهێنانی CID
    cid_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{clean_name}/cids/JSON"
    try:
        cid_res = session.get(cid_url, timeout=10)
        if cid_res.status_code != 200:
            return None, "ماددەکە نەدۆزرایەوە (هەڵەی سێرڤەر)."
        cid = cid_res.json()["IdentifierList"]["CID"][0]
        
        # ٢. بەدەستهێنانی زانیارییەکان
        prop_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/property/Title,MolecularFormula,MolecularWeight,XLogP3/JSON"
        prop_res = session.get(prop_url, timeout=10)
        prop_data = prop_res.json()
        
        # ئەم بەشە گرنگە: پشکنینی بوونی PropertyTable
        if "PropertyTable" in prop_data:
            return prop_data["PropertyTable"]["Properties"][0], None
        else:
            return None, "داتای ماددەکە لە PubChem بوونی نییە."
            
    except Exception as e:
        return None, f"کێشە لە پەیوەندی: {str(e)}"

ingredient = st.text_input("ناوی ماددە (بە ئینگلیزی):")

if st.button("شیکردنەوە"):
    if ingredient:
        with st.spinner('خەریکی هێنانی داتام...'):
            data, error = get_molecular_data(ingredient)
            if data:
                st.success("سەرکەوتوو بوو!")
                st.table(pd.DataFrame([data]))
            else:
                st.error(error)



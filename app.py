
import streamlit as st
import pandas as pd
import requests
import urllib.parse

# ڕێکخستنی لاپەڕەکە
st.set_page_config(page_title="LAV LAB - Chemical Data", layout="wide")
st.title("🧪 LAV LAB: Molecular Data Engine")

# لێرەدا Cache بەکاردێنین بۆ ئەوەی زۆر داواکاری نەنێرین
@st.cache_data(ttl=3600)
def get_pubchem_data(name):
    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"})
    
    clean_name = urllib.parse.quote(name.strip())
    cid_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{clean_name}/cids/JSON"
    
    try:
        cid_res = session.get(cid_url, timeout=10)
        if cid_res.status_code != 200: return None
        cid = cid_res.json()["IdentifierList"]["CID"][0]
        
        prop_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/property/Title,MolecularFormula,MolecularWeight,XLogP3/JSON"
        prop_res = session.get(prop_url, timeout=10)
        return prop_res.json()["PropertyTable"]["Properties"][0]
    except:
        return None

ingredient_input = st.text_input("ناوی ماددەکە (بۆ نموونە: Niacinamide):")

if st.button("شیکردنەوە"):
    if ingredient_input:
        with st.spinner('سەرقاڵی گەڕان...'):
            data = get_pubchem_data(ingredient_input)
            if data:
                st.success("سەرکەوتوو بوو!")
                st.table(pd.DataFrame([data]))
            else:
                st.error("نەتوانرا داتا بدۆزرێتەوە! یان ماددەکە بوونی نییە، یان PubChem بلۆکی کردووین. وشەی 'Caffeine' تاقیبکەرەوە.")



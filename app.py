
import streamlit as st
import pandas as pd
import requests
import urllib.parse

# ڕێکخستنی لاپەڕە
st.set_page_config(page_title="LAV LAB - Chemical Data", layout="centered")
st.title("🧪 LAV LAB: Molecular Data Engine")

@st.cache_data(ttl=86400)
def fetch_data(name):
    # پاککردنەوەی ناوی ماددەکە
    safe_name = urllib.parse.quote(name.strip())
    url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{safe_name}/property/Title,MolecularFormula,MolecularWeight,XLogP3/JSON"
    
    try:
        # بەکارهێنانی User-Agent بۆ ئەوەی وەک ڕۆبۆت دەرنەکەوین
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            return response.json()["PropertyTable"]["Properties"][0]
    except Exception as e:
        return None
    return None

# دیزاینی ناوەوە
name = st.text_input("ناوی ماددە (بە ئینگلیزی) بنووسە:")
if st.button("شیکردنەوەی زانستی"):
    if name:
        with st.spinner('خەریکی پرۆسێسکردنم...'):
            data = fetch_data(name)
            if data:
                st.success("سەرکەوتوو بوو:")
                st.table(pd.DataFrame([data]))
            else:
                st.error("ماددەکە نەدۆزرایەوە، دڵنیابە لە ناوەکە (بە ئینگلیزی بێت).")


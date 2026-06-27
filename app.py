
import streamlit as st
import pandas as pd
import requests
from fake_useragent import UserAgent

# ڕێکخستنی لاپەڕەکە
st.set_page_config(page_title="LAV LAB - Chemical Data", layout="wide")
st.title("🧪 LAV LAB: Molecular Data Engine")

# دروستکردنی Session
session = requests.Session()
ua = UserAgent()

def get_molecular_data(name):
    name = name.strip()
    
    # هەر جارەی ناسنامەیەکی نوێ و ڕاستەقینە بۆ سێرڤەر دەنێرین
    headers = {"User-Agent": ua.random}
    
    # هەنگاوی ١: دۆزینەوەی CID
    cid_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{name}/cids/JSON"
    
    try:
        response = session.get(cid_url, headers=headers, timeout=15)
        if response.status_code != 200:
            return None, f"نەتوانرا ناوی '{name}' لە PubChem بدۆزرێتەوە (هەڵەی: {response.status_code})"
        
        data = response.json()
        if "IdentifierList" not in data or "CID" not in data["IdentifierList"]:
            return None, "ئەم ماددەیە لە داتابەیسدا نەدۆزرایەوە."
            
        cid = data["IdentifierList"]["CID"][0]
        
        # هەنگاوی ٢: بەدەستهێنانی زانیارییەکان بە CID
        prop_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/property/Title,MolecularFormula,MolecularWeight,XLogP3/JSON"
        prop_res = session.get(prop_url, headers=headers, timeout=15)
        prop_data = prop_res.json()
        
        if "PropertyTable" in prop_data and "Properties" in prop_data["PropertyTable"]:
            return prop_data["PropertyTable"]["Properties"][0], None
        else:
            return None, "زانیارییەکان بۆ ئەم ماددەیە بەردەست نین."
            
    except Exception as e:
        return None, f"هەڵەی تەکنیکی: {str(e)}"

# بەشی بەکارهێنەر
ingredient = st.text_input("ناوی ماددە (بە ئینگلیزی، بۆ نموونە: Niacinamide):")

if st.button("شیکردنەوەی زانستی"):
    if ingredient:
        with st.spinner('خەریکی پرۆسێسکردنی ماددەکەم...'):
            data, error = get_molecular_data(ingredient)
            if data:
                st.success("سەرکەوتوو بوو!")
                df = pd.DataFrame([data])
                st.table(df)
            else:
                st.error(f"کێشەیەک ڕوویدا: {error}")
    else:
        st.warning("تکایە ناوی ماددەیەک بنووسە.")


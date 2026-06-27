
import streamlit as st
import pandas as pd
import requests
import urllib.parse

st.set_page_config(page_title="LAV LAB - Chemical Data", layout="wide")
st.title("🧪 LAV LAB: Molecular Data Engine")

# دروستکردنی Session بۆ بەهێزکردنی پەیوەندییەکان
session = requests.Session()
session.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"})

def get_molecular_data(name):
    # پاککردنەوەی ناو
    name = name.strip()
    clean_name = urllib.parse.quote(name)
    
    # هەنگاوی ١: دۆزینەوەی CID
    cid_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{clean_name}/cids/JSON"
    try:
        cid_res = session.get(cid_url, timeout=10)
        # ئەگەر 404 بوو واتە ناوی ماددەکە هەڵەیە یان PubChem ناناسێت
        if cid_res.status_code != 200:
            return None, f"نەتوانرا ناوی '{name}' لە PubChem بدۆزرێتەوە."
        
        cid_data = cid_res.json()
        if "IdentifierList" not in cid_data or not cid_data["IdentifierList"].get("CID"):
            return None, "ئەم ماددەیە لە داتابەیسدا نییە."
            
        cid = cid_data["IdentifierList"]["CID"][0]
        
        # هەنگاوی ٢: بەدەستهێنانی زانیارییەکان
        prop_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/property/Title,MolecularFormula,MolecularWeight,XLogP3/JSON"
        prop_res = session.get(prop_url, timeout=10)
        prop_data = prop_res.json()
        
        if "PropertyTable" in prop_data:
            return prop_data["PropertyTable"]["Properties"][0], None
        else:
            return None, "زانیارییەکان بۆ ئەم ماددەیە بەردەست نین."
            
    except Exception as e:
        return None, f"هەڵەی تەکنیکی: {str(e)}"

# دیزاینی وێبگەڕ
ingredient = st.text_input("ناوی ماددە (بە ئینگلیزی، بۆ نموونە: Niacinamide):")

if st.button("شیکردنەوەی زانستی"):
    if ingredient:
        with st.spinner('خەریکی پرۆسێسکردنی ماددەکەم...'):
            data, error = get_molecular_data(ingredient)
            if data:
                st.success("سەرکەوتوو بوو!")
                # نمایشکردنی داتا بە ستایڵێکی جوان
                st.table(pd.DataFrame([data]))
            else:
                st.error(error)



```python
import streamlit as st
import pandas as pd
import requests

# پڕۆسەی وەرگرتنی داتا لە PubChem
def get_chemical_data(name):
    name = name.strip().lower()
    # URL بۆ وەرگرتنی زانیارییە گشتییەکان
    url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{name}/property/Title,MolecularFormula,MolecularWeight,XLogP3/JSON"
    
    # خۆمان وەک وێبگەڕێکی ئاسایی نیشان دەدەین بۆ ڕێگریکردن لە بلۆک بوون
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        # ئەگەر داواکارییەکە سەرکەوتوو بوو
        if response.status_code == 200:
            data = response.json()
            if "PropertyTable" in data and "Properties" in data["PropertyTable"]:
                return pd.DataFrame(data["PropertyTable"]["Properties"])
            return None
        else:
            return None
    except Exception:
        # گەڕاندنەوەی None لە کاتی هەر هەڵەیەکدا
        return None

# دیزاینی لاپەڕەکە
st.title("🧪 LAV LAB: Molecular Data")
substance = st.text_input("ناوی ماددە بنووسە (بۆ نموونە: Aspirin):")

if st.button("شیکردنەوە"):
    if substance:
        with st.spinner('خەریکی هێنانی داتام...'):
            df = get_chemical_data(substance)
            
            if df is not None and not df.empty:
                st.success("داتاکە بە سەرکەوتوویی دۆزرایەوە:")
                st.table(df)
            else:
                st.error("نەتوانرا داتا وەربگیرێت. دڵنیابە لە ناوەکە (بە ئینگلیزی) یان ناوی زانستی بەکاربهێنە.")
    else:
        st.warning("تکایە ناوی ماددەیەک بنووسە.")

```

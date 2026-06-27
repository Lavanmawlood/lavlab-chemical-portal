
import streamlit as st
import pandas as pd
import requests

# دیزاینی وێبگەڕ
st.set_page_config(page_title="LAV LAB - Chemical Data", layout="wide")
st.title("🧪 LAV LAB: Molecular Data Engine")

# دروستکردنی Session بۆ بەهێزکردنی پەیوەندییەکان
session = requests.Session()
session.headers.update({"User-Agent": "Mozilla/5.0"})

def get_molecular_data(name):
    name = name.strip()
    
    # هەنگاوی ١: دۆزینەوەی CID بە بەکارهێنانی PUG REST
    # تێبینی: پەیڕەوی 'name_to_cid' باشترە لە گەڕانی گشتی
    cid_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{name}/cids/JSON"
    
    try:
        response = session.get(cid_url, timeout=15)
        if response.status_code != 200:
            return None, f"نەتوانرا ناوی '{name}' لە PubChem بدۆزرێتەوە (هەڵەی: {response.status_code})"
        
        data = response.json()
        if "IdentifierList" not in data or "CID" not in data["IdentifierList"]:
            return None, "ئەم ماددەیە لە داتابەیسدا نەدۆزرایەوە."
            
        cid = data["IdentifierList"]["CID"][0]
        
        # هەنگاوی ٢: بەدەستهێنانی زانیارییەکان بە CID
        prop_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/property/Title,MolecularFormula,MolecularWeight,XLogP3/JSON"
        prop_res = session.get(prop_url, timeout=15)
        prop_data = prop_res.json()
        
        if "PropertyTable" in prop_data and "Properties" in prop_data["PropertyTable"]:
            return prop_data["PropertyTable"]["Properties"][0], None
        else:
            return None, "زانیارییەکان بۆ ئەم ماددەیە بەردەست نین، تکایە ناوی ماددەیەکی تر تاقیبکەرەوە."
            
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
                # نمایشکردنی داتا بە خشتە
                df = pd.DataFrame([data])
                st.table(df)
            else:
                # نیشاندانی هەڵە بە شێوەیەکی جوان
                st.error(f"کێشەیەک ڕوویدا: {error}")
    else:
        st.warning("تکایە ناوی ماددەیەک بنووسە.")



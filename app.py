
import streamlit as st
import pandas as pd
import json
import urllib.request
import urllib.parse

st.set_page_config(page_title="LAV LAB - Professional Engine", layout="wide")
st.title("🧪 LAV LAB: Molecular Data Professional")

# هێدەری فەرمی بۆ تێپەڕاندنی سیکیوریتی پوبچێم
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

def get_data(name):
    clean_name = urllib.parse.quote(name.strip())
    # URL بۆ وەرگرتنی زانیارییەکان
    url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{clean_name}/property/Title,MolecularFormula,MolecularWeight,XLogP3/JSON"
    
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=10) as response:
            res = json.loads(response.read().decode('utf-8'))
            props = res["PropertyTable"]["Properties"][0]
            return {
                "Title": props.get("Title", name),
                "Formula": props.get("MolecularFormula", "N/A"),
                "Weight": props.get("MolecularWeight", "N/A"),
                "LogP": props.get("XLogP3", "N/A")
            }
    except Exception as e:
        return None

query = st.text_input("ناوی ماددە بنووسە (بە ئینگلیزی):")
if st.button("شیکردنەوە"):
    if query:
        data = get_data(query)
        if data:
            st.success(f"داتای {data['Title']} دۆزرایەوە:")
            df = pd.DataFrame([data])
            st.table(df)
        else:
            st.error("داوای لێبوردن دەکەین، ماددەکە نەدۆزرایەوە. دڵنیا ببەوە لە ڕێنووسەکەی.")
    else:
        st.warning("تکایە ناوی ماددەیەک بنووسە.")

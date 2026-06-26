
import streamlit as st
import pandas as pd
import requests
import urllib.parse

st.set_page_config(page_title="LAV LAB - Professional Engine", layout="wide")
st.title("🧪 LAV LAB: Molecular Data Professional")

# داتابەیسی لۆکاڵی بەهێزکراو - بۆ ئەو کاتانەی سێرڤەر داتا نادات
LOCAL_DB = {
    "lactic acid": {"Title": "Lactic acid", "Formula": "C3H6O3", "Weight": "90.08", "LogP": "-0.6"},
    "niacinamide": {"Title": "Niacinamide", "Formula": "C6H6N2O", "Weight": "122.12", "LogP": "-0.4"},
    "glycolic acid": {"Title": "Glycolic acid", "Formula": "C2H4O3", "Weight": "76.05", "LogP": "-1.1"},
    "hyaluronic acid": {"Title": "Hyaluronic acid", "Formula": "C28H44N2O23", "Weight": "776.6", "LogP": "N/A"}
}

def get_data(name):
    name = name.strip().lower()
    # گەڕان لە لۆکاڵی
    if name in LOCAL_DB:
        return LOCAL_DB[name]
    
    # گەڕان لە PubChem
    try:
        url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{urllib.parse.quote(name)}/property/Title,MolecularFormula,MolecularWeight,XLogP3/JSON"
        res = requests.get(url, timeout=5).json()
        props = res["PropertyTable"]["Properties"][0]
        return {
            "Title": props.get("Title", name),
            "Formula": props.get("MolecularFormula", "N/A"),
            "Weight": props.get("MolecularWeight", "N/A"),
            "LogP": props.get("XLogP3", "N/A")
        }
    except:
        return None

query = st.text_input("ناوی ماددە بنووسە:")
if st.button("شیکردنەوە"):
    data = get_data(query)
    if data:
        df = pd.DataFrame([data])
        st.table(df)
    else:
        st.error("داوای لێبوردن دەکەین، هیچ زانیارییەک بۆ ئەم ماددەیە نەدۆزرایەوە.")


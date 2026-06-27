
import streamlit as st
import pandas as pd
import json
import urllib.request
import urllib.parse

st.set_page_config(page_title="LAV LAB - Chemical Data", layout="wide")
st.title("🧪 LAV LAB: Molecular Data Professional")

# بەکارهێنانی هێدەری Browser ی ڕاستەقینە بۆ ئەوەی بلۆک نەبیت
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def get_data(name):
    clean_name = urllib.parse.quote(name.strip())
    # URL بۆ کێشانی داتا
    url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{clean_name}/property/Title,MolecularFormula,MolecularWeight,XLogP3/JSON"
    
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=15) as response:
            res = json.loads(response.read().decode('utf-8'))
            props = res["PropertyTable"]["Properties"][0]
            return {
                "Title": props.get("Title", name),
                "Formula": props.get("MolecularFormula", "N/A"),
                "Weight": f"{props.get('MolecularWeight', 'N/A')} g/mol",
                "LogP": props.get("XLogP3", "N/A")
            }
    except Exception as e:
        # ئەگەر کێشەی پەیوەندی هەبوو، لێرەدا دەگەڕێتەوە
        return None

query = st.text_input("ناوی ماددە بنووسە (بۆ نموونە: Niacinamide, Retinol):")

if st.button("شیکردنەوە"):
    if query:
        with st.spinner('خەریکی پەیوەندیکردنم بە داتابەیسی پوبچێم...'):
            data = get_data(query)
            if data:
                st.success(f"زانیاری بۆ '{data['Title']}' دۆزرایەوە:")
                df = pd.DataFrame([data])
                st.table(df)
            else:
                st.error(f"ئای! نەتوانرا پەیوەندی بە پوبچێم بکرێت یان ماددەکە نەدۆزرایەوە. تکایە دووبارە تاقی بکەرەوە.")
    else:
        st.warning("تکایە ناوی ماددەیەک بنووسە.")

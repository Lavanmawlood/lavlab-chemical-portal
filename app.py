
Import streamlit as st
import pandas as pd
import json
import urllib.request
import urllib.parse

st.set_page_config(page_title="LAV LAB - Chemical Data", layout="wide")
st.title("🧪 LAV LAB: Molecular Data Engine")

# ئەم هێدەرە وادەکات سێرڤەرەکە وەک وێبگەڕێکی ئاسایی (وەک کرۆم) بتناسێت
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

def fetch_pubchem(name):
    clean_name = urllib.parse.quote(name.strip())
    # URL بۆ وەرگرتنی CID
    cid_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{clean_name}/cids/JSON"
    
    try:
        req = urllib.request.Request(cid_url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=10) as response:
            cid_data = json.loads(response.read().decode('utf-8'))
            cid = cid_data["IdentifierList"]["CID"][0]
            
        # URL بۆ وەرگرتنی تایبەتمەندییەکان
        prop_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/property/Title,MolecularFormula,MolecularWeight,XLogP3/JSON"
        req_prop = urllib.request.Request(prop_url, headers=HEADERS)
        with urllib.request.urlopen(req_prop, timeout=10) as response_prop:
            prop_data = json.loads(response_prop.read().decode('utf-8'))
            return {"status": "success", "data": prop_data["PropertyTable"]["Properties"][0]}
            
    except Exception as e:
        return {"status": "error", "message": str(e)}

ingredient_input = st.text_input("ناوی ماددەکە بنووسە (بۆ نموونە: Niacinamide):")

if st.button("شیکردنەوە"):
    if ingredient_input:
        with st.spinner('کۆکردنەوەی زانیارییەکان لە PubChem...'):
            result = fetch_pubchem(ingredient_input)
            
            if result["status"] == "success":
                st.success("داتاکان دۆزرانەوە:")
                df = pd.DataFrame([result["data"]])
                st.table(df)
                
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button("📥 داگرتنی داتا وەک CSV", csv, "chemical_data.csv", "text/csv")
            else:
                st.error("نەتوانرا زانیاری بۆ ئەم ماددەیە بدۆزرێتەوە، دڵنیا ببەوە لە ناوی دروستی ماددەکە.")
    else:
        st.warning("تکایە ناوی ماددەیەک بنووسە.")

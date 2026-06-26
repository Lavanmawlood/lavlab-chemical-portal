
import streamlit as st
import pandas as pd
import requests
import urllib.parse

st.set_page_config(page_title="LAV LAB - Raw Data Engine", layout="wide")
st.title("🧪 LAV LAB: Raw Data Explorer")

def get_raw_data(compound):
    clean_name = urllib.parse.quote(compound.strip())
    # یەکەم داواکاری بۆ CID
    url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{clean_name}/cids/JSON"
    try:
        response = requests.get(url, timeout=10).json()
        cid = response["IdentifierList"]["CID"][0]
        
        # دووەم داواکاری بۆ هەموو داتا بەردەستەکان
        url_data = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/property/Title,MolecularFormula,MolecularWeight,XLogP3,IUPACName/JSON"
        prop_response = requests.get(url_data, timeout=10).json()
        return prop_response["PropertyTable"]["Properties"][0]
    except Exception as e:
        return {"Error": str(e)}

input_text = st.text_input("ناوی ماددەکە بنووسە:")
if st.button("شیکردنەوەی تەواو"):
    if input_text:
        data = get_raw_data(input_text)
        st.write("### داتای خاوی وەرگیراو لە سێرڤەر:")
        st.json(data) # ئەمە هەموو شتێک کە سێرڤەرەکە بیدات پیشانی دەدات
        
        if "CID" in data:
            st.image(f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{data['CID']}/PNG")



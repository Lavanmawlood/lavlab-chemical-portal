
import streamlit as st
import pandas as pd
import requests
import urllib.parse
import time
import random

st.set_page_config(page_title="LAV LAB - Advanced Scraper", layout="wide")
st.title("🧪 LAV LAB: Advanced Molecular Scraper")

# بەکارهێنانی لیستێک لە User-Agents بۆ ئەوەی هەر جارەی وەک وێبگەڕێک دەربکەوین
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
]

def perform_scraping(name):
    # کێشانی ناوی ماددەکە بۆ URL
    clean_name = urllib.parse.quote(name.strip())
    
    # ئامادەکردنی سێشن بە User-Agentـی هەڕەمەکی
    session = requests.Session()
    session.headers.update({"User-Agent": random.choice(USER_AGENTS)})
    
    try:
        # هەنگاوی ١: دۆزینەوەی CID (بەکارهێنانی پشووی هەڕەمەکی بۆ ئەوەی بە ڕۆبۆت نەبینرێین)
        time.sleep(random.uniform(1.5, 3.0)) 
        cid_res = session.get(f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{clean_name}/cids/JSON", timeout=15)
        
        if cid_res.status_code != 200:
            return None, f"هەڵەی سێرڤەر: {cid_res.status_code}"
            
        cid = cid_res.json()["IdentifierList"]["CID"][0]
        
        # هەنگاوی ٢: وەرگرتنی زانیارییەکان
        time.sleep(random.uniform(1.0, 2.0))
        prop_res = session.get(f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/property/Title,MolecularFormula,MolecularWeight,XLogP3/JSON", timeout=15)
        
        return prop_res.json()["PropertyTable"]["Properties"][0], None
    except Exception as e:
        return None, str(e)

ingredient = st.text_input("ناوی ماددەکە بنووسە:")

if st.button("سکراپکردن دەستپێبکە"):
    if ingredient:
        with st.spinner('خەریکی سکراپکردنم...'):
            data, error = perform_scraping(ingredient)
            if data:
                st.success("سەرکەوتوویی!")
                st.dataframe(pd.DataFrame([data]))
            else:
                st.error(f"سکراپینگ سەرکەوتوو نەبوو: {error}")

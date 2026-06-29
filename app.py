
import streamlit as st
import pandas as pd
import requests
import sqlite3
import os

# ١. دامەزراندنی داتابەیس
def init_db():
    conn = sqlite3.connect('chemical_data.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS chemicals 
                 (name TEXT PRIMARY KEY, data TEXT)''')
    conn.commit()
    conn.close()

init_db()

# ٢. پشکنینی داتابەیس یان API
def get_chemical(name):
    name = name.lower().strip()
    conn = sqlite3.connect('chemical_data.db')
    c = conn.cursor()
    c.execute("SELECT data FROM chemicals WHERE name=?", (name,))
    row = c.fetchone()
    
    if row:
        conn.close()
        return pd.read_json(row[0]) # گەڕاندنەوەی داتا لە داتابەیس
    
    # ئەگەر لە داتابەیس نەبوو، بچۆ بۆ API
    api_key = os.environ.get("PUBCHEM_API_KEY")
    url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{name}/property/Title,MolecularFormula,MolecularWeight,XLogP3/JSON?api_key={api_key}"
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()["PropertyTable"]["Properties"][0]
            df = pd.DataFrame([data])
            # سەیڤکردنی لە داتابەیس بۆ جارانی داهاتوو
            c.execute("INSERT INTO chemicals VALUES (?, ?)", (name, df.to_json()))
            conn.commit()
            conn.close()
            return df
    except:
        pass
    conn.close()
    return None

# دیزاینی ئەپەکە
st.title("🧪 LAV LAB: Molecular Engine")
name = st.text_input("ناوی ماددە بنووسە:")
if st.button("شیکردنەوە"):
    with st.spinner('خەریکی گەڕانم...'):
        result = get_chemical(name)
        if result is not None:
            st.table(result)
        else:
            st.error("ماددەکە نەدۆزرایەوە.")

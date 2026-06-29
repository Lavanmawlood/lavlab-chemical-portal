
import streamlit as st
import pandas as pd
import requests
import sqlite3
import os

# Initialize Database
def init_db():
    with sqlite3.connect('chemical_data.db') as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS chemicals 
                     (name TEXT PRIMARY KEY, data TEXT)''')

init_db()

def get_chemical(name):
    name = name.lower().strip()
    
    # Check Database
    with sqlite3.connect('chemical_data.db') as conn:
        cursor = conn.execute("SELECT data FROM chemicals WHERE name=?", (name,))
        row = cursor.fetchone()
        if row:
            return pd.read_json(row[0]), True

    # API Request
    api_key = os.environ.get("PUBCHEM_API_KEY")
    url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{name}/property/Title,MolecularFormula,MolecularWeight,XLogP3/JSON"
    params = {'api_key': api_key} if api_key else {}
    
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            content = response.json()
            # لێرەدا دڵنیا دەبینەوە کە داتاکە هەیە پێش ئەوەی بیکەین بە DataFrame
            if "PropertyTable" in content and "Properties" in content["PropertyTable"]:
                properties = content["PropertyTable"]["Properties"]
                if properties:
                    df = pd.DataFrame(properties)
                    with sqlite3.connect('chemical_data.db') as conn:
                        conn.execute("INSERT OR REPLACE INTO chemicals VALUES (?, ?)", (name, df.to_json()))
                    return df, False
    except Exception as e:
        return None, False
    return None, False

# UI Design
st.title("🧪 LAV LAB: Molecular Engine")
name = st.text_input("Enter substance name (e.g., Aspirin, Nicotinamide):")

if st.button("Analyze"):
    if name:
        with st.spinner('Fetching molecular data...'):
            result, from_db = get_chemical(name)
            if result is not None:
                st.success("Data found successfully!")
                st.table(result)
            else:
                st.error("No data found for this substance. Check the spelling or try a scientific name.")


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
    
    # Check local database
    with sqlite3.connect('chemical_data.db') as conn:
        cursor = conn.execute("SELECT data FROM chemicals WHERE name=?", (name,))
        row = cursor.fetchone()
        if row:
            return pd.read_json(row[0]), True

    # API Request - Only requesting Title first to ensure existence
    api_key = os.environ.get("PUBCHEM_API_KEY")
    url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{name}/property/Title,MolecularFormula,MolecularWeight,XLogP3/JSON"
    params = {'api_key': api_key} if api_key else {}
    
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json().get("PropertyTable", {}).get("Properties", [])
            if data:
                df = pd.DataFrame(data) # We keep all properties returned
                with sqlite3.connect('chemical_data.db') as conn:
                    conn.execute("INSERT OR REPLACE INTO chemicals VALUES (?, ?)", (name, df.to_json()))
                return df, False
    except Exception as e:
        st.error(f"Error: {e}")
    return None, False

# UI Design
st.title("🧪 LAV LAB: Molecular Engine")
name = st.text_input("Enter the name of the substance (in English):")

if st.button("Analyze"):
    if name:
        with st.spinner('Analyzing...'):
            result, from_db = get_chemical(name)
            if result is not None:
                st.success("Substance Found!")
                st.table(result)
            else:
                st.error("Substance not found. Note: PubChem is very specific about names (e.g., use 'Nicotinamide' instead of 'Niacinamide').")

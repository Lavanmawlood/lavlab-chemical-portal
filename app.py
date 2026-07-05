
import streamlit as st
import os
from pymongo import MongoClient

# بەکارهێنانی کلیلە نهێنییەکەی Hugging Face
mongo_uri = os.getenv("MONGO_URI")

st.title("🧪 LAV LAB: Molecular Engine")

if not mongo_uri:
    st.error("تکایە MONGO_URI لە بەشی Secrets-ی Hugging Face دابنێ!")
else:
    try:
        # پەیوەندی کردن بە داتابەیس
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
        db = client['LAV_LAB']['chemicals']
        st.success("پەیوەندی بە داتابەیسەوە سەرکەوتوو بوو!")
        
        ingredient = st.text_input("ناوی ماددە (بە ئینگلیزی):")
        if st.button("شیکردنەوە"):
            result = db.find_one({'Title': {'$regex': ingredient, '$options': 'i'}})
            if result:
                st.write(result)
            else:
                st.error("ماددەکە نەدۆزرایەوە.")
    except Exception as e:
        st.error(f"هەڵە: {e}")


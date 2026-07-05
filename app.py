
import streamlit as st
import os
from pymongo import MongoClient

# بەکارهێنانی ژینگەی نهێنی بۆ پاراستنی پاسۆردەکەت
# دڵنیابە لە Hugging Face لە بەشی Secrets ناوی MONGO_URI-ت بەکارهێناوە
MONGO_URI = os.getenv("MONGO_URI")

@st.cache_resource
def get_db():
    try:
        client = MongoClient(MONGO_URI)
        # لێرە ناوی داتابەیس و کۆڵێکشنەکەت دیاری بکە
        return client['LAV_LAB']['chemicals']
    except Exception as e:
        st.error(f"هەڵە لە پەیوەندی کردن بە داتابەیس: {e}")
        return None

db = get_db()

st.title("🧪 LAV LAB: Molecular Engine")
st.write("بەخێر بێن بۆ سیستەمی شیکردنەوەی ماددە کیمیاییەکان")

ingredient = st.text_input("ناوی ماددە (بە ئینگلیزی):")

if st.button("شیکردنەوە"):
    if ingredient and db is not None:
        # گەڕان لەناو MongoDB بە شێوەیەکی زیرەک
        result = db.find_one({'Title': {'$regex': ingredient, '$options': 'i'}})
        
        if result:
            st.success("داتاکە دۆزرایەوە!")
            st.json(result)
        else:
            st.error("ئەم ماددەیە لە داتابەیسدا نییە. تکایە پێشتر لە ڕێگەی سکراپەرەکەتەوە داتاکەی تێ بکە.")
    elif not ingredient:
        st.warning("تکایە ناوی ماددەیەک بنووسە.")


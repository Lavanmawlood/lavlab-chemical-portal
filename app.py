
import streamlit as st
import os
from pymongo import MongoClient

# چارەسەری کێشەی Permission Denied: ڕێگری لە دروستکردنی فایل لە شوێنی نەگونجاو
os.environ["STREAMLIT_SERVER_FILE_WATCHER_TYPE"] = "none"
os.environ["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] = "false"

# ڕێکخستنی سەرەتایی لاپەڕەکە
st.set_page_config(
    page_title="LAV LAB: Molecular Engine",
    page_icon="🧪",
    layout="wide"
)

# هێنانی MONGO_URI لە سکرێتەکانەوە
MONGO_URI = os.getenv("MONGO_URI")

# بەکارهێنانی caching بۆ خێراکردنی پەیوەندی
@st.cache_resource
def get_mongo_client(uri):
    if not uri:
        return None
    try:
        # پەیوەندی کردن بە داتابەیس بە شێوەیەکی ستاندارد
        client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        client.server_info()
        return client
    except Exception:
        return None

client = get_mongo_client(MONGO_URI)

# CSS بۆ دیزاین
st.markdown("""
    <style>
        .chemical-card { background-color: #1E293B; padding: 20px; border-radius: 12px; border-left: 5px solid #3B82F6; margin-bottom: 15px; }
    </style>
""", unsafe_allow_html=True)

st.title("🧪 LAV LAB: Molecular Engine v2.0")

if not client:
    st.error("❌ پەیوەندی بە داتابەیسەوە نەکرا. دڵنیا بەرەوە لە ڕاستی MONGO_URI لە بەشی Secrets.")
else:
    db = client['LAV_LAB']['chemicals']
    ingredient = st.text_input("ناوی ماددە کیمیاییەکە بنووسە:").strip()
    
    if st.button("شیکردنەوە"):
        if ingredient:
            result = db.find_one({'Title': {'$regex': ingredient, '$options': 'i'}})
            if result:
                st.markdown(f"""
                <div class='chemical-card'>
                    <h2 style='color:#60A5FA;'>{result.get('Title')}</h2>
                    <p><b>فورمۆڵا:</b> {result.get('Formula')}</p>
                    <p><b>کێش:</b> {result.get('MolecularWeight')} g/mol</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.warning("ماددەکە نەدۆزرایەوە.")

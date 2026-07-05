
import streamlit as st
import os
from pymongo import MongoClient

# تێکۆشین بۆ هێنانی مۆنگۆ یو ئاڕ ئای بە شێوازێکی پارێزراو
MONGO_URI = os.getenv("MONGO_URI")

# ڕێکخستنی سەرەتایی لاپەڕەکە بۆ دیزاینێکی مۆدێرن و عەرەب
st.set_page_config(
    page_title="LAV LAB: Molecular Engine",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# هێنان و پاراستنی بەستەری داتابەیس بە شێوازی کاش (Connection Pooling)
# ئەم فەنکشنە تەنها یەکجار کۆنێکشن دروست دەکات و لە میمۆریدا دەیهێڵێتەوە
@st.cache_resource
def get_mongo_client(uri):
    if not uri:
        return None
    try:
        # بەستنەوە بە بەکارهێنانی تایم‌ئاوت و ڕێگەدان بە بڕوانامەی ئێس ئێس ئێڵ (SSL)
        client = MongoClient(
            uri, 
            tlsAllowInvalidCertificates=True, 
            serverSelectionTimeoutMS=8000
        )
        # دڵنیابوونەوە لە بەستەرەکە بە هێنانی زانیاری سێرڤەر
        client.server_info()
        return client
    except Exception as e:
        st.error(f"⚠️ هەڵە لە دروستکردنی پەیوەندی داتابەیس: {e}")
        return None

# دەستپێکردنی کۆنێکشنەکە
client = get_mongo_client(MONGO_URI)

# دەستکاریکردنی ستایلی ئەپەکە بە CSS بۆ ئەوەی زۆر بەرز و پڕۆفیشناڵ دەرکەوێت
st.markdown("""
    <style>
        .chemical-card {
            background-color: #1E293B;
            padding: 20px;
            border-radius: 12px;
            border-left: 5px solid #3B82F6;
            margin-bottom: 15px;
        }
        .safety-badge {
            background-color: #EF4444;
            color: white;
            padding: 4px 10px;
            border-radius: 6px;
            font-size: 14px;
            font-weight: bold;
        }
        .stButton>button {
            background-color: #3B82F6 !important;
            color: white !important;
            border-radius: 8px !important;
            width: 100%;
        }
    </style>
""", unsafe_allow_html=True)

# تایتڵی سەرەکی پڕۆژەکە
st.title("🧪 LAV LAB: Molecular Engine v2.0")
st.subheader("سیستەمی زیرەکی ئەندازیاری داتای ماددە کیمیایی و جوانکارییەکان")

if not MONGO_URI:
    st.error("🚨 کلیل یان ناونیشانی MONGO_URI لە بەشی Secrets یان Environment بەردەست نییە!")
elif client is None:
    st.error("❌ ناتوانرێت پەیوەندی بە داتابەیسی دەمەقاڵێکراو (MongoDB) بکریت. تکایە ئایپی یان کلیلەکەت تاقیکەرەوە.")
else:
    # دیاریکردنی داتابەیس و کۆڵێکشن
    db = client['LAV_LAB']['chemicals']
    
    st.success("✅ بەستەر بە داتابەیسی نێودەوڵەتی سەرکەوتوو بوو (Connected).")
    
    # لایەنەکانی گەڕان
    col1, col2 = st.columns([3, 1])
    
    with col1:
        ingredient_input = st.text_input(
            "ناوی توخم یان ماددەی کیمیایی بنووسە (بۆ نموونە: Caffeine یان Retinol):",
            placeholder="Search for ingredients..."
        ).strip()
        
    with col2:
        st.write("##") # بۆ هاوتەریب کردنی دوگمەکە
        search_button = st.button("شیکردنەوەی مۆلیکولار")
        
    if search_button and ingredient_input:
        # لێرەدا گەڕان بە شێوازێکی خێرا و پشتگوێخستنی گەورە و بچووکی پیتەکان دەکەین
        with st.spinner("خەریکی پشکنینی داتابەیسی مۆلیکولارین..."):
            result = db.find_one({'Title': {'$regex': f"^{ingredient_input}$", '$options': 'i'}})
            
            # ئەگەر ناوی تەواو نەبوو، گەڕانێکی گشتی تر ئەنجام دەدەین وەک پلان بی (Plan B)
            if not result:
                result = db.find_one({'Title': {'$regex': ingredient_input, '$options': 'i'}})
                
            if result:
                st.markdown("### 📊 ئەنجامی شیکردنەوەی زانستی:")
                
                # جیاکردنەوەی داتاکان بە شێوازێکی زۆر مۆدێرن و ڕێکخراو
                title = result.get('Title', 'Unknown Chemical')
                formula = result.get('Formula', 'N/A')
                mw = result.get('MolecularWeight', 'N/A')
                safety = result.get('Safety', 'Safe under recommended usage')
                description = result.get('Description', 'هیچ پێناسەیەک لە داتابەیسدا تۆمار نەکراوە.')
                
                # پیشاندانی زانیارییەکان لە دیمەنێکی مۆدێرندا
                st.markdown(f"""
                <div class="chemical-card">
                    <h2 style='color: #60A5FA; margin-top: 0;'>🧪 {title}</h2>
                    <p><b>فورمۆڵای کیمیایی (Chemical Formula):</b> <code style='color: #34D399;'>{formula}</code></p>
                    <p><b>کێشی مۆلیکولار (Molecular Weight):</b> {mw} g/mol</p>
                    <p><b>وەسفی ماددە (Description):</b> {description}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # دابەشکردنی لایەنی سەلامەتی و زانیاری تر بە تابهینەر (Tabs)
                tab1, tab2 = st.tabs(["🔒 پڕۆفایلی سەلامەتی (Safety)", "🛠️ ڕێنمایی کارلێککردن"])
                
                with tab1:
                    st.markdown(f"### 🛡️ پڕۆفایلی زانستی بۆ سەلامەتی ماددەکە:")
                    st.info(safety)
                    
                with tab2:
                    st.markdown("### ⚠️ کارلێککردنە مۆلیکولارییەکان (Interactions):")
                    st.warning("تکایە دڵنیابەرەوە لە بەکارنەهێنانی ئەم ماددەیە لەگەڵ ترشە بەهێزەکان یان تێکەڵکردنی بێ ڕاوێژی زانستی پێشوەختە.")
                    
            else:
                st.error(f"🔍 ماددەی '{ingredient_input}' لە داتابەیسەکەتدا نەدۆزرایەوە. تکایە دڵنیابە لە ناوەکەی، یان لە ڕێگەی سکراپەرەوە زیادی بکە.")


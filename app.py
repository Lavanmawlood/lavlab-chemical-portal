import os
# ئەم دوو دێڕە ڕێگری لە دروستکردنی فایلی زیادە دەکات کە ئیرۆری Permission دەدات
os.environ["STREAMLIT_SERVER_FILE_WATCHER_TYPE"] = "none"
os.environ["STREAMLIT_SERVER_HEADLESS"] = "true"

import streamlit as st
st.set_page_config(layout="wide")

# پاشان کۆدی مۆنگۆ و شتەکانی ترت بنووسە...

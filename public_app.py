import streamlit as st  # これが必要です！

# --- 以前お渡しした「自動検索コード」を使う場合 ---
import os

st.set_page_config(page_title="競艇Pro", layout="wide")
st.title("🏁 会場を選択")

col1, col2, col3,col4,col5 = st.columns(3)

with col1:
    if st.button("桐生", use_container_width=True):
        # 候補となるパスをすべて試す
        targets = [
            "pages/07_gamagori.py",
            "pages/pages/07_gamagori.py",
            "07_gamagori.py"
with col1:
     if st.button("蒲郡", use_container_width=True):
        # 候補となるパスをすべて試す
        targets = [
            "pages/07_gamagori.py",
            "pages/pages/07_gamagori.py",
            "07_gamagori.py"
        ]
        
        found = False
        for path in targets:
            if os.path.exists(path):
                st.switch_page(path)
                found = True
                break
        
        if not found:
            st.error("ファイルが見つかりません。")



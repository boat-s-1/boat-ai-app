import streamlit as st  # これが必要です！

# --- 以前お渡しした「自動検索コード」を使う場合 ---
import streamlit as st

st.set_page_config(page_title="競艇Pro", layout="wide")

st.title("🏁 会場を選択")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("蒲郡", use_container_width=True):
        st.switch_page("pages/07_gamagori.py")

with col2:
    if st.button("大村", use_container_width=True):
        st.switch_page("pages/01_omura.py")

with col3:
    if st.button("常滑", use_container_width=True):
        st.switch_page("pages/02_tokoname.py")
        ]
        
        found = False
        for path in targets:
            if os.path.exists(path):
                st.switch_page(path)
                found = True
                break
        
        if not found:
            st.error("ファイルが見つかりません。")




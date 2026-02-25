import streamlit as st  # これが必要です！

# --- 以前お渡しした「自動検索コード」を使う場合 ---
import streamlit as st

st.set_page_config(page_title="競艇Pro", layout="wide")

st.title("🏁 会場を選択")

col1, col2, col3, col4, col5, col6, col7 = st.columns(7)

with col1:
    if st.button("桐生01", use_container_width=True):
        st.switch_page("pages/01_kiryu.py")

with col2:
    if st.button("戸田02", use_container_width=True):
        st.switch_page("pages/02_toda.py")

with col3:
    if st.button("江戸川03", use_container_width=True):
        st.switch_page("pages/03_edogawa.py")

with col4:
    if st.button("平和島04", use_container_width=True):
        st.switch_page("pages/04_heiwajima.py")

with col5:
    if st.button("多摩川05", use_container_width=True):
        st.switch_page("pages/05_tamagawa.py")

with col6:
    if st.button("浜名湖06", use_container_width=True):
        st.switch_page("pages/06_hamanako.py")

with col7:
    if st.button("蒲郡07", use_container_width=True):
        st.switch_page("pages/02_tokoname.py")
        
        found = False
        for path in targets:
            if os.path.exists(path):
                st.switch_page(path)
                found = True
                break
        
        if not found:
            st.error("ファイルが見つかりません。")







import streamlit as st

st.set_page_config(page_title="競艇Pro", layout="wide")

st.title("🏁 会場を選択")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("蒲郡", use_container_width=True):
        st.switch_page("07_gamagori")












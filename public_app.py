import streamlit as st

st.set_page_config(page_title="競艇Pro", layout="wide")

st.title("🏁 会場を選択")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("蒲郡", use_container_width=True):
        st.switch_page("pages/07_蒲郡.py")

with col2:
    if st.button("大村", use_container_width=True):
        st.switch_page("pages/02_大村.py")

with col3:
    if st.button("住之江", use_container_width=True):
        st.switch_page("pages/03_住之江.py")

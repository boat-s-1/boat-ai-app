import streamlit as st

# 1. 必ず最初に書く
st.set_page_config(page_title="競艇Pro", layout="wide")

st.title("🏁 会場を選択（テスト表示）")

# 動作確認用に1つだけボタンを置く
if st.button("テスト：桐生", use_container_width=True):
    st.switch_page("pages/01_kiryu.py")

st.write("この文字が見えていれば、基本設定は正常です！")

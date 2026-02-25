import streamlit as st

# 1. 念のため「./」をつけて、現在の場所から探すことを明示する
# もしくは、ファイル名が「01_kiryu.py」で合っているか再確認してください
try:
    page_01 = st.Page("pages/01_kiryu.py", title="桐生競艇場", icon="🚤")
    page_02 = st.Page("pages/02_toda.py", title="戸田競艇場", icon="🌊")
    page_07 = st.Page("pages/07_gamagori.py", title="蒲郡競艇場", icon="🏁")

    # ナビゲーション設定
    pg = st.navigation([page_01, page_02, page_07])
    pg.run()

except Exception as e:
    # どこでエラーが出ているか、画面にヒントを出します
    st.error(f"エラーが発生しました: {e}")
    import os
    st.write("現在見えているファイル一覧:", os.listdir("pages") if os.path.exists("pages") else "pagesフォルダがありません")

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
        st.switch_page("pages/07_gamagori.py")


